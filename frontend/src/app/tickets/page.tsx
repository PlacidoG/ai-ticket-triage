

export default function TicketsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold">Tickets</h1>
        <p className="text-muted-foreground">
          View and manage all support tickets
        </p>
      </div>
      <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
        Ticket list coming on Day 10
      </div>
    </div>
  );
}