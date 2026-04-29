
export default function TicketDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold">Ticket Detail</h1>
        <p className="text-muted-foreground">Ticket ID: {params.id}</p>
      </div>
      <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
        Ticket detail view coming on Day 11
      </div>
    </div>
  );
}