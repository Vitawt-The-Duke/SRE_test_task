import http from "k6/http";
import { sleep } from "k6";

export default function () {
  http.get("http://app:8080/work?latencyMs=200&failRatePct=5");
  sleep(0.1);
}
