import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    return NextResponse.json({ error: 'GITHUB_TOKEN not configured' }, { status: 500 });
  }

  const now = new Date();
  const currentYear = now.getFullYear();
  const from = `${currentYear}-01-01T00:00:00Z`;
  const to = now.toISOString();

  const query = `
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
              }
            }
          }
        }
      }
    }
  `;

  try {
    const response = await fetch('https://api.github.com/graphql', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables: { login: 'nachopalmeri', from, to },
      }),
      next: { revalidate: 3600 },
    });

    const data = await response.json();

    if (data.errors) {
      return NextResponse.json({ error: data.errors[0].message }, { status: 400 });
    }

    const collection = data.data?.user?.contributionsCollection;
    const calendar = collection?.contributionCalendar;

    return NextResponse.json({
      totalContributions: calendar?.totalContributions || 0,
      totalCommits: (collection?.totalCommitContributions || 0) + (collection?.restrictedContributionsCount || 0),
      weeks: calendar?.weeks || [],
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch GitHub data' }, { status: 500 });
  }
}
