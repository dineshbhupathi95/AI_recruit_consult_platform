import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Loader2, Settings, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { getErrorMessage } from "@/services/apiClient";
import { settingsService } from "@/services/settingsService";
import type { SettingFieldSchema } from "@/types/settings";

const SOURCE_LABELS = {
  tenant: "Saved in settings",
  environment: "From environment",
  default: "Default",
} as const;

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [provider, setProvider] = useState("");
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const { data: schema, isLoading: schemaLoading } = useQuery({
    queryKey: ["settings", "schema"],
    queryFn: settingsService.getSchema,
  });

  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: settingsService.getSettings,
  });

  const selectedProvider = useMemo(
    () => schema?.ai_providers.find((p) => p.id === provider),
    [schema, provider]
  );

  const activeFields = useMemo(() => {
    if (!selectedProvider || !schema) return [];
    return [...selectedProvider.fields, ...schema.common_ai_fields];
  }, [selectedProvider, schema]);

  useEffect(() => {
    if (!settings || !schema) return;
    setProvider(settings.ai_provider);
    const initial: Record<string, string> = {};
    for (const item of settings.values) {
      if (item.value != null) {
        initial[item.key] = String(item.value);
      }
    }
    setFormValues(initial);
  }, [settings, schema]);

  const handleProviderChange = (nextProvider: string) => {
    setProvider(nextProvider);
    setTestResult(null);
    if (!schema || !settings) return;

    const next = schema.ai_providers.find((p) => p.id === nextProvider);
    if (!next) return;

    const fields = [...next.fields, ...schema.common_ai_fields];
    const nextValues: Record<string, string> = {};
    for (const field of fields) {
      const existing = settings.values.find((v) => v.key === field.key);
      if (existing?.value != null) {
        nextValues[field.key] = String(existing.value);
      } else if (field.default != null) {
        nextValues[field.key] = String(field.default);
      }
    }
    setFormValues(nextValues);
  };

  const saveMutation = useMutation({
    mutationFn: () =>
      settingsService.updateSettings({
        ai_provider: provider,
        values: Object.fromEntries(
          activeFields.map((field) => {
            const raw = formValues[field.key] ?? "";
            if (field.type === "number") {
              return [field.key, raw === "" ? null : Number(raw)];
            }
            return [field.key, raw === "" ? null : raw];
          })
        ),
      }),
    onSuccess: () => {
      setError(null);
      setTestResult(null);
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const testMutation = useMutation({
    mutationFn: settingsService.testAIConnection,
    onSuccess: (result) => setTestResult({ success: result.success, message: result.message }),
    onError: (err) => setTestResult({ success: false, message: getErrorMessage(err) }),
  });

  const getFieldMeta = (key: string) => settings?.values.find((v) => v.key === key);

  const renderField = (field: SettingFieldSchema) => {
    const meta = getFieldMeta(field.key);
    const value = formValues[field.key] ?? "";
    const isPassword = field.type === "password";

    return (
      <div key={field.key} className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Label htmlFor={field.key}>{field.label}</Label>
          {meta && (
            <Badge variant="outline" className="text-[10px] font-normal">
              {SOURCE_LABELS[meta.source]}
            </Badge>
          )}
        </div>
        <Input
          id={field.key}
          type={isPassword ? "password" : field.type === "number" ? "number" : "text"}
          value={value}
          placeholder={
            isPassword && meta?.is_set
              ? "Leave blank to keep current value"
              : field.placeholder ?? (field.env_var ? `Env: ${field.env_var}` : undefined)
          }
          onChange={(e) => setFormValues((prev) => ({ ...prev, [field.key]: e.target.value }))}
        />
        {field.env_var && (
          <p className="text-xs text-muted-foreground">Environment variable: {field.env_var}</p>
        )}
      </div>
    );
  };

  if (schemaLoading || settingsLoading) {
    return <div className="py-12 text-center text-muted-foreground">Loading settings...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <Settings className="h-7 w-7" />
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        </div>
        <p className="text-muted-foreground">
          Configure AI provider credentials and platform integrations for your organization
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>AI Provider</CardTitle>
          <CardDescription>
            Choose a provider and enter credentials. Tenant settings override environment variables.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
          )}

          <div className="space-y-2">
            <Label htmlFor="ai_provider">Provider</Label>
            <Select
              id="ai_provider"
              value={provider}
              onChange={(e) => handleProviderChange(e.target.value)}
            >
              {schema?.ai_providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </Select>
            {selectedProvider && (
              <p className="text-sm text-muted-foreground">{selectedProvider.description}</p>
            )}
          </div>

          {activeFields.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2">{activeFields.map(renderField)}</div>
          )}

          {provider === "mock" && (
            <p className="rounded-md bg-muted p-3 text-sm text-muted-foreground">
              Mock provider returns deterministic test data. No API key required.
            </p>
          )}

          <div className="flex flex-wrap gap-3">
            <Button disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
              {saveMutation.isPending ? "Saving..." : "Save Settings"}
            </Button>
            <Button
              variant="outline"
              disabled={testMutation.isPending}
              onClick={() => testMutation.mutate()}
            >
              {testMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Testing...
                </>
              ) : (
                "Test Connection"
              )}
            </Button>
          </div>

          {testResult && (
            <div
              className={`flex items-start gap-2 rounded-md p-3 text-sm ${
                testResult.success ? "bg-green-500/10 text-green-700 dark:text-green-400" : "bg-destructive/10 text-destructive"
              }`}
            >
              {testResult.success ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
              ) : (
                <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}

          {settings?.updated_at && (
            <p className="text-xs text-muted-foreground">
              Last updated: {new Date(settings.updated_at).toLocaleString()}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
