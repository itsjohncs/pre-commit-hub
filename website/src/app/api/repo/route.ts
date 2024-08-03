import {NextResponse} from "next/server";
import {Octokit} from "@octokit/core";
import {z} from "zod";

import prisma from "#root/prisma";
import {Prisma} from "@prisma/client";

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

        try {
            const repo = await prisma.repo.create({data: {id}});
            return NextResponse.json(repo);
        } catch (error) {
            if (
                error instanceof Prisma.PrismaClientKnownRequestError &&
                error.code === "P2002"
            ) {
                return NextResponse.json(
                    {error: "Repository already exists in the database"},
                    {status: 409},
                );
            }
            throw error;
        }
    } catch (error) {
        console.error("Error processing request:", error);
        return NextResponse.json(
            {error: "An error occurred while processing the request"},
            {status: 500},
        );
    }
}
