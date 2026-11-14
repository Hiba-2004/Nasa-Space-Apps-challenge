
const API_BASE_URL = "http://localhost:8000/api/v1";

export async function getAstronautMeasurements(astronautId: string) {
  const response = await fetch(
    `${API_BASE_URL}/astronauts/${astronautId}/measurements`
  );

  if (!response.ok) {
    throw new Error("Unable to fetch astronaut measurements");
  }

  return response.json();
}

export async function createMeasurement(
  astronautId: string,
  measurement: {
    measured_at: string;
    metric: string;
    value: number;
    unit: string;
    source: string;
  }
) {
  const response = await fetch(
    `${API_BASE_URL}/astronauts/${astronautId}/measurements`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(measurement),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Unable to save measurement");
  }

  return response.json();
}

export async function getAstronautAssessments(astronautId: string) {
  const response = await fetch(
    `${API_BASE_URL}/astronauts/${astronautId}/assessments`
  );

  if (!response.ok) {
    throw new Error("Unable to fetch astronaut assessments");
  }

  return response.json();
}

export async function createAstronautAssessment(astronautId: string) {
  const response = await fetch(
    `${API_BASE_URL}/astronauts/${astronautId}/assessments`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Unable to create health assessment");
  }

  return response.json();
}

// NEW: Fetch astronaut health check-ins
export async function getAstronautCheckins(astronautId: string) {
  const response = await fetch(
    `${API_BASE_URL}/astronauts/${astronautId}/checkins`
  );

  if (!response.ok) {
    throw new Error("Unable to fetch astronaut check-ins");
  }

  return response.json();
}
