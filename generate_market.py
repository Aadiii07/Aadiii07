import os
import random
import requests
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


USERNAME = "Aadiii07"
TOKEN = os.environ.get("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def get_contributions():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=100"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    events = response.json()

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=59)

    contributions = {
        start_date + timedelta(days=i): 0
        for i in range(60)
    }

    for event in events:
        created_at = datetime.strptime(
            event["created_at"],
            "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        if created_at not in contributions:
            continue

        if event["type"] == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            contributions[created_at] += max(len(commits), 1)

        elif event["type"] in {
            "PullRequestEvent",
            "IssuesEvent",
            "CreateEvent",
            "PullRequestReviewEvent"
        }:
            contributions[created_at] += 1

    return contributions


def generate_candles(contributions):
    candles = []
    previous_close = 0

    for date, contribution_count in contributions.items():
        open_value = previous_close
        close_value = contribution_count

        high_value = max(open_value, close_value)

        if contribution_count > 0:
            high_value += random.uniform(0.2, 0.8)

        low_value = max(
            0,
            min(open_value, close_value) - random.uniform(0.0, 0.4)
        )

        candles.append(
            (
                date,
                open_value,
                high_value,
                low_value,
                close_value
            )
        )

        previous_close = close_value

    return candles


def draw_chart(candles):
    plt.figure(figsize=(10, 3.8))

    axis = plt.gca()

    for date, open_value, high_value, low_value, close_value in candles:
        x = mdates.date2num(date)

        rising = close_value >= open_value
        candle_color = "#2DA44E" if rising else "#CF222E"

        axis.plot(
            [x, x],
            [low_value, high_value],
            linewidth=1,
            color=candle_color
        )

        body_bottom = min(open_value, close_value)
        body_height = abs(close_value - open_value)

        if body_height == 0:
            body_height = 0.08

        candle = Rectangle(
            (x - 0.28, body_bottom),
            0.56,
            body_height,
            facecolor=candle_color,
            edgecolor=candle_color
        )

        axis.add_patch(candle)

    axis.xaxis_date()

    axis.xaxis.set_major_locator(
        mdates.DayLocator(interval=7)
    )

    axis.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %d")
    )

    plt.title(
        f"{USERNAME}'s Contribution Market — Last 60 Days"
    )

    plt.ylabel("Contributions")

    plt.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.35
    )

    plt.tight_layout()

    os.makedirs("assets", exist_ok=True)

    plt.savefig(
        "assets/contribution-market.svg",
        format="svg",
        bbox_inches="tight",
        transparent=True
    )

    plt.close()


if __name__ == "__main__":
    contributions = get_contributions()
    candles = generate_candles(contributions)
    draw_chart(candles)

    print("Contribution market generated.")
