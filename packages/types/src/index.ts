export type HealthLiveResponse = {
  status: "ok";
  service: "creatoros-api";
};

export type HealthReadyResponse = {
  status: "ready" | "not_ready";
  database: "ok" | "unavailable";
  redis: "ok" | "unavailable";
  request_id?: string | null;
};
