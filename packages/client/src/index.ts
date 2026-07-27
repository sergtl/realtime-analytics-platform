type AnalyticsClientOptions = {
  apiKey: string;
  endpoint?: string;
  source?: string;
};

type TrackOptions = {
  eventId?: string;
  timestamp?: string;
  correlationId?: string;
  schemaVersion?: "1.0.0";
};

export class AnalyticsClient {
  private apiKey: string;
  private endpoint: string;
  private source: string;

  constructor(options: AnalyticsClientOptions) {
    this.apiKey = options.apiKey;
    this.endpoint = options.endpoint ?? "http://localhost:8000";
    this.source = options.source ?? "web";
  }

  async track(
    eventType: string,
    payload: Record<string, unknown> = {},
    options: TrackOptions = {},
  ) {
    const response = await fetch(`${this.endpoint}/track`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        event_type: eventType,
        source: this.source,
        schema_version: options.schemaVersion ?? "1.0.0",
        ...(options.eventId ? { event_id: options.eventId } : {}),
        ...(options.timestamp ? { event_id: options.timestamp } : {}),
        ...(options.correlationId
          ? { correlation_id: options.correlationId }
          : {}),
        payload,
      }),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }
}

export function createAnalyticsClient(options: AnalyticsClientOptions) {
  return new AnalyticsClient(options);
}
