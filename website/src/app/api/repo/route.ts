import {NextResponse} from "next/server";
import {Octokit} from "@octokit/core";
import {z} from "zod";

import prisma from "#root/prisma";

const octokit = new Octokit({auth: process.env.GITHUB_TOKEN});

const RepoSchema = z.object({
    owner: z.string().min(1),
    name: z.string().min(1),
});

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const result = RepoSchema.safeParse(body);

        if (!result.success) {
            return NextResponse.json(
                {error: "Invalid input", details: result.error.format()},
                {status: 400},
            );
        }

        const {owner, name} = result.data;
        const response = await octokit.graphql(
            `
            query($owner: String!, $name: String!) {
                repository(owner: $owner, name: $name) {
                    id
                }
            }`,
            {owner, name},
        );
        const id = (response as any).repository.id;

        const repo = await prisma.repo.create({data: {id}});

        return NextResponse.json(repo);
    } catch (error) {
        console.error("Error processing request:", error);
        return NextResponse.json(
            {error: "An error occurred while processing the request"},
            {status: 500},
        );
    }
}
