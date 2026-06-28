import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  ArrowLeft,
  Briefcase,
  Building2,
  Calendar,
  Edit,
  Globe,
  Mail,
  MapPin,
  Pencil,
  Phone,
  Plus,
  Trash2,
  User,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ClientStatusBadge } from "@/components/clients/ClientStatusBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Tabs } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  contactFormSchema,
  locationFormSchema,
  noteFormSchema,
  type ContactFormValues,
  type LocationFormValues,
  type NoteFormValues,
} from "@/forms/clientSchemas";
import { clientService } from "@/services/clientService";
import { jobService } from "@/services/jobService";
import { CONTACT_TYPE_LABELS, type ClientContact } from "@/types/client";
import { JOB_STATUS_LABELS } from "@/types/job";

type TabId = "overview" | "contacts" | "locations" | "notes" | "requirements";

export function ClientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [showContactForm, setShowContactForm] = useState(false);
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [showNoteForm, setShowNoteForm] = useState(false);
  const [editingContactId, setEditingContactId] = useState<string | null>(null);
  const [editingLocationId, setEditingLocationId] = useState<string | null>(null);

  const { data: client, isLoading } = useQuery({
    queryKey: ["clients", id],
    queryFn: () => clientService.getById(id!),
    enabled: !!id,
  });

  const { data: clientJobs } = useQuery({
    queryKey: ["jobs", { client_id: id }],
    queryFn: () => jobService.list({ client_id: id, page_size: 10 }),
    enabled: !!id && activeTab === "requirements",
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["clients", id] });

  const deleteMutation = useMutation({
    mutationFn: () => clientService.delete(id!),
    onSuccess: () => navigate("/clients"),
  });

  const addContactMutation = useMutation({
    mutationFn: clientService.addContact.bind(null, id!),
    onSuccess: () => { invalidate(); setShowContactForm(false); },
  });

  const updateContactMutation = useMutation({
    mutationFn: ({ contactId, data }: { contactId: string; data: ContactFormValues }) =>
      clientService.updateContact(id!, contactId, data),
    onSuccess: () => { invalidate(); setEditingContactId(null); },
  });

  const deleteContactMutation = useMutation({
    mutationFn: (contactId: string) => clientService.deleteContact(id!, contactId),
    onSuccess: invalidate,
  });

  const addLocationMutation = useMutation({
    mutationFn: clientService.addLocation.bind(null, id!),
    onSuccess: () => { invalidate(); setShowLocationForm(false); },
  });

  const updateLocationMutation = useMutation({
    mutationFn: ({ locationId, data }: { locationId: string; data: LocationFormValues }) =>
      clientService.updateLocation(id!, locationId, data),
    onSuccess: () => { invalidate(); setEditingLocationId(null); },
  });

  const deleteLocationMutation = useMutation({
    mutationFn: (locationId: string) => clientService.deleteLocation(id!, locationId),
    onSuccess: invalidate,
  });

  const addNoteMutation = useMutation({
    mutationFn: clientService.addNote.bind(null, id!),
    onSuccess: () => { invalidate(); setShowNoteForm(false); },
  });

  if (isLoading) {
    return <div className="py-12 text-center text-muted-foreground">Loading client...</div>;
  }

  if (!client) {
    return <div className="py-12 text-center text-destructive">Client not found</div>;
  }

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "contacts", label: "Contacts", count: client.contacts.length },
    { id: "locations", label: "Locations", count: client.locations.length },
    { id: "notes", label: "Notes", count: client.notes.length },
    { id: "requirements", label: "Requirements" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <Link to="/clients">
            <Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button>
          </Link>
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold tracking-tight">{client.name}</h1>
              <ClientStatusBadge status={client.status} />
            </div>
            <p className="text-muted-foreground">{client.industry ?? "No industry specified"}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Updated {new Date(client.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/clients/${id}/edit`}>
            <Button variant="outline"><Edit className="h-4 w-4" />Edit</Button>
          </Link>
          <Link to={`/jobs/new?client_id=${id}`}>
            <Button variant="outline"><Briefcase className="h-4 w-4" />Add Job</Button>
          </Link>
          <Button
            variant="destructive"
            size="icon"
            onClick={() => {
              if (confirm("Delete this client? This cannot be undone.")) deleteMutation.mutate();
            }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={(t) => setActiveTab(t as TabId)} />

      {activeTab === "overview" && (
        <div className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />Company Information
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <InfoField label="Legal Name" value={client.legal_name} />
              <InfoField label="Industry" value={client.industry} />
              <InfoField label="Email" value={client.email} icon={Mail} />
              <InfoField label="Phone" value={client.phone} icon={Phone} />
              <div className="sm:col-span-2">
                {client.website ? (
                  <div className="flex items-start gap-2">
                    <Globe className="mt-0.5 h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Website</p>
                      <a href={client.website} target="_blank" rel="noopener noreferrer" className="font-medium text-primary hover:underline">
                        {client.website}
                      </a>
                    </div>
                  </div>
                ) : (
                  <InfoField label="Website" value={null} />
                )}
              </div>
              <div className="sm:col-span-2">
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="mt-1">{client.description ?? "—"}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <SummaryRow label="Contacts" value={client.contacts.length} />
              <SummaryRow label="Locations" value={client.locations.length} />
              <SummaryRow label="Hiring Managers" value={client.contacts.filter((c) => c.contact_type === "hiring_manager").length} />
              <SummaryRow label="Notes" value={client.notes.length} />
              <div className="flex items-center gap-2 pt-2 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                Created {new Date(client.created_at).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === "contacts" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2"><User className="h-5 w-5" />Contacts</CardTitle>
              <CardDescription>Hiring managers and key contacts</CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={() => { setShowContactForm(true); setEditingContactId(null); }}>
              <Plus className="h-4 w-4" />Add Contact
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {showContactForm && (
              <ContactFormInline
                onSubmit={(data) => addContactMutation.mutateAsync(data)}
                isSubmitting={addContactMutation.isPending}
                onCancel={() => setShowContactForm(false)}
              />
            )}
            {client.contacts.length === 0 && !showContactForm ? (
              <p className="text-sm text-muted-foreground">No contacts yet.</p>
            ) : (
              client.contacts.map((contact) =>
                editingContactId === contact.id ? (
                  <ContactFormInline
                    key={contact.id}
                    defaultValues={contactToFormValues(contact)}
                    submitLabel="Save Contact"
                    onSubmit={(data) => updateContactMutation.mutateAsync({ contactId: contact.id, data })}
                    isSubmitting={updateContactMutation.isPending}
                    onCancel={() => setEditingContactId(null)}
                  />
                ) : (
                  <div key={contact.id} className="flex items-start justify-between rounded-md border border-border p-4">
                    <div>
                      <p className="font-medium">{contact.full_name}</p>
                      <p className="text-sm text-muted-foreground">{contact.job_title ?? "—"}{contact.department && ` · ${contact.department}`}</p>
                      <p className="text-sm">{contact.email}</p>
                      {contact.phone && <p className="text-sm text-muted-foreground">{contact.phone}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{CONTACT_TYPE_LABELS[contact.contact_type]}</Badge>
                      <Button variant="ghost" size="icon" onClick={() => setEditingContactId(contact.id)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => { if (confirm("Delete contact?")) deleteContactMutation.mutate(contact.id); }}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                    </div>
                  </div>
                )
              )
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === "locations" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2"><MapPin className="h-5 w-5" />Locations</CardTitle>
              <CardDescription>Office locations and addresses</CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={() => { setShowLocationForm(true); setEditingLocationId(null); }}>
              <Plus className="h-4 w-4" />Add Location
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {showLocationForm && (
              <LocationFormInline onSubmit={(data) => addLocationMutation.mutateAsync(data)} isSubmitting={addLocationMutation.isPending} onCancel={() => setShowLocationForm(false)} />
            )}
            <div className="grid gap-3 sm:grid-cols-2">
              {client.locations.map((location) =>
                editingLocationId === location.id ? (
                  <LocationFormInline key={location.id} defaultValues={locationToFormValues(location)} submitLabel="Save Location"
                    onSubmit={(data) => updateLocationMutation.mutateAsync({ locationId: location.id, data })}
                    isSubmitting={updateLocationMutation.isPending} onCancel={() => setEditingLocationId(null)} />
                ) : (
                  <div key={location.id} className="rounded-md border border-border p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{location.name}</p>
                          {location.is_headquarters && <Badge variant="secondary">HQ</Badge>}
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {[location.address_line1, location.city, location.state, location.country].filter(Boolean).join(", ") || "—"}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" onClick={() => setEditingLocationId(location.id)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => { if (confirm("Delete location?")) deleteLocationMutation.mutate(location.id); }}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
            {client.locations.length === 0 && !showLocationForm && <p className="text-sm text-muted-foreground">No locations yet.</p>}
          </CardContent>
        </Card>
      )}

      {activeTab === "notes" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div><CardTitle>Notes</CardTitle><CardDescription>Internal notes and observations</CardDescription></div>
            <Button size="sm" variant="outline" onClick={() => setShowNoteForm(!showNoteForm)}><Plus className="h-4 w-4" />Add Note</Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {showNoteForm && <NoteFormInline onSubmit={(data) => addNoteMutation.mutateAsync(data)} isSubmitting={addNoteMutation.isPending} onCancel={() => setShowNoteForm(false)} />}
            {client.notes.map((note) => (
              <div key={note.id} className="rounded-md border border-border p-4">
                <p className="text-sm whitespace-pre-wrap">{note.content}</p>
                <p className="mt-2 text-xs text-muted-foreground">{new Date(note.created_at).toLocaleString()}</p>
              </div>
            ))}
            {client.notes.length === 0 && !showNoteForm && <p className="text-sm text-muted-foreground">No notes yet.</p>}
          </CardContent>
        </Card>
      )}

      {activeTab === "requirements" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div><CardTitle>Job Requirements</CardTitle><CardDescription>Open positions for this client</CardDescription></div>
            <Link to={`/jobs/new?client_id=${id}`}>
              <Button size="sm"><Plus className="h-4 w-4" />Add Requirement</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {clientJobs?.items.length ? (
              <div className="divide-y divide-border">
                {clientJobs.items.map((job) => (
                  <Link key={job.id} to={`/jobs/${job.id}`} className="flex items-center justify-between py-3 hover:bg-muted/30 -mx-2 px-2 rounded-md">
                    <div>
                      <p className="font-medium">{job.title}</p>
                      <p className="text-sm text-muted-foreground">{JOB_STATUS_LABELS[job.status]} · {job.required_skills_count} required skills</p>
                    </div>
                    <Badge variant="outline">{job.priority}</Badge>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No job requirements for this client yet.</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function InfoField({ label, value, icon: Icon }: { label: string; value: string | null | undefined; icon?: typeof Mail }) {
  return (
    <div className={Icon ? "flex items-start gap-2" : ""}>
      {Icon && <Icon className="mt-0.5 h-4 w-4 text-muted-foreground" />}
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="font-medium">{value ?? "—"}</p>
      </div>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: number }) {
  return (<div className="flex justify-between"><span className="text-muted-foreground">{label}</span><span className="font-medium">{value}</span></div>);
}

function contactToFormValues(contact: ClientContact): ContactFormValues {
  return { first_name: contact.first_name, last_name: contact.last_name, email: contact.email, phone: contact.phone ?? "", job_title: contact.job_title ?? "", department: contact.department ?? "", contact_type: contact.contact_type, is_active: contact.is_active };
}

function locationToFormValues(location: { name: string; address_line1: string | null; address_line2: string | null; city: string | null; state: string | null; country: string | null; postal_code: string | null; is_headquarters: boolean }): LocationFormValues {
  return { name: location.name, address_line1: location.address_line1 ?? "", address_line2: location.address_line2 ?? "", city: location.city ?? "", state: location.state ?? "", country: location.country ?? "", postal_code: location.postal_code ?? "", is_headquarters: location.is_headquarters };
}

function ContactFormInline({ onSubmit, isSubmitting, onCancel, defaultValues, submitLabel = "Add Contact" }: { onSubmit: (data: ContactFormValues) => Promise<unknown>; isSubmitting: boolean; onCancel: () => void; defaultValues?: ContactFormValues; submitLabel?: string }) {
  const { register, handleSubmit, formState: { errors } } = useForm<ContactFormValues>({ resolver: zodResolver(contactFormSchema), defaultValues: defaultValues ?? { contact_type: "general", is_active: true } });
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="rounded-md border border-border bg-muted/30 p-4 space-y-3">
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="First Name" error={errors.first_name?.message}><Input {...register("first_name")} /></Field>
        <Field label="Last Name" error={errors.last_name?.message}><Input {...register("last_name")} /></Field>
        <Field label="Email" error={errors.email?.message}><Input type="email" {...register("email")} /></Field>
        <Field label="Phone"><Input {...register("phone")} /></Field>
        <Field label="Job Title"><Input {...register("job_title")} /></Field>
        <Field label="Department"><Input {...register("department")} /></Field>
        <Field label="Contact Type"><Select {...register("contact_type")}><option value="general">General</option><option value="hiring_manager">Hiring Manager</option><option value="primary">Primary Contact</option></Select></Field>
      </div>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={isSubmitting}>{isSubmitting ? "Saving..." : submitLabel}</Button>
        <Button type="button" size="sm" variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
}

function LocationFormInline({ onSubmit, isSubmitting, onCancel, defaultValues, submitLabel = "Add Location" }: { onSubmit: (data: LocationFormValues) => Promise<unknown>; isSubmitting: boolean; onCancel: () => void; defaultValues?: LocationFormValues; submitLabel?: string }) {
  const { register, handleSubmit, formState: { errors } } = useForm<LocationFormValues>({ resolver: zodResolver(locationFormSchema), defaultValues: defaultValues ?? { is_headquarters: false } });
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="rounded-md border border-border bg-muted/30 p-4 space-y-3 sm:col-span-2">
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Location Name" error={errors.name?.message}><Input {...register("name")} /></Field>
        <Field label="City"><Input {...register("city")} /></Field>
        <Field label="State"><Input {...register("state")} /></Field>
        <Field label="Country"><Input {...register("country")} /></Field>
        <Field label="Address"><Input {...register("address_line1")} /></Field>
        <Field label="Postal Code"><Input {...register("postal_code")} /></Field>
      </div>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" {...register("is_headquarters")} />Headquarters</label>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={isSubmitting}>{isSubmitting ? "Saving..." : submitLabel}</Button>
        <Button type="button" size="sm" variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
}

function NoteFormInline({ onSubmit, isSubmitting, onCancel }: { onSubmit: (data: NoteFormValues) => Promise<unknown>; isSubmitting: boolean; onCancel: () => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<NoteFormValues>({ resolver: zodResolver(noteFormSchema) });
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="rounded-md border border-border bg-muted/30 p-4 space-y-3">
      <Field label="Note" error={errors.content?.message}><Textarea {...register("content")} rows={3} placeholder="Add a note..." /></Field>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={isSubmitting}>{isSubmitting ? "Adding..." : "Add Note"}</Button>
        <Button type="button" size="sm" variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (<div className="space-y-1"><Label>{label}</Label>{children}{error && <p className="text-xs text-destructive">{error}</p>}</div>);
}
