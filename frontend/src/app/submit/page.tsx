import { TicketForm } from "@/components/ticket-form";

export default function SubmitPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold">Submit Ticket</h1>
        <p className="text-muted-foreground">
          Describe your issue and our AI will classify and prioritize it
          automatically
        </p>
      </div>
      <TicketForm />
    </div>
  );
}