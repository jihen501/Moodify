

const baseUrl = "http://localhost:5000";

export async function fetchWeeklyStats(userId: string) {
    const res = await fetch(baseUrl +`/weekly_stats/${userId}`);
    console.log("Fetching stats for user:", userId);
    if (!res.ok) throw new Error("Erreur lors de la récupération des stats");
    return res.json();
}

export async function fetchCurentRecommendations() {
    const res = await fetch(baseUrl + `/recommendations`);
    console.log("Fetching recommendations for user:");
    if (!res.ok) throw new Error("Erreur lors de la récupération des recommandations");
    return res.json();
}
  