import type { HealthLiveResponse } from "@creatoros/types";
import { API_PATHS } from "@creatoros/shared";
import { apiGet } from "./client";

export async function getApiHealth(): Promise<HealthLiveResponse> {
  return apiGet<HealthLiveResponse>(API_PATHS.health);
}
