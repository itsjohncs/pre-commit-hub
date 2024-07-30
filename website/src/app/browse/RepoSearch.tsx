"use client";

import classNames from "classnames";
import {CgSpinner as SpinnerIcon} from "react-icons/cg";
import {RiErrorWarningLine as ErrorIcon} from "react-icons/ri";
import {FaRegCircleCheck as OkIcon} from "react-icons/fa6";
import {Octokit} from "octokit";
import React, {useEffect, useRef, useState} from "react";
import {useDebounceCallback} from "usehooks-ts";

function parseDescriptor(descriptor: string): {owner: string; name: string} {
    const parts = descriptor.split("/");
    if (parts.length !== 2) {
        throw new ValidationError(
            'Invalid repo descriptor. Expected "owner/repo".',
        );
    }
    return {owner: parts[0], name: parts[1]};
}

class ValidationError extends Error {}

async function isRepoValid(
    octokit: Octokit,
    owner: string,
    name: string,
): Promise<true> {
    const result = await octokit.rest.repos.getContent({
        owner,
        repo: name,
        path: ".pre-commit-hooks.yaml",
    });

    const data = result.data;
    if (!Array.isArray(data) && data.type === "file" && data.size > 0) {
        return true;
    }

    throw new ValidationError(
        "Repo does not have valid `.pre-commit-hooks.yaml` file.",
    );
}

interface Props {
    className?: string;
}

type ValidationState =
    | {state: "idle"}
    | {state: "pending"}
    | {state: "ok"}
    | {state: "error"; message: string};

export default function RepoSearch(props: Props) {
    const octokitRef = useRef<Octokit>();
    useEffect(function () {
        octokitRef.current = new Octokit();
    }, []);

    const lockIdRef = useRef<number>(0);

    const [validation, setValidation] = useState<ValidationState>({
        state: "idle",
    });

    const debouncedValidate = useDebounceCallback(async function (
        expectedLockId: number,
        owner: string,
        name: string,
    ) {
        if (lockIdRef.current !== expectedLockId) {
            return;
        }

        setValidation({state: "pending"});

        let result: true | string;
        try {
            result = await isRepoValid(octokitRef.current!, owner, name);
        } catch (e) {
            if (e instanceof ValidationError) {
                result = e.message;
            } else {
                console.error(
                    `Got unexpected error validating repo ${owner}/${name}`,
                    e,
                );
                result = "Unexpected error validating repo.";
            }
        }

        if (lockIdRef.current === expectedLockId) {
            if (typeof result === "string") {
                setValidation({state: "error", message: result});
            } else {
                setValidation({state: "ok"});
            }
        }
    });

    const handleInput = function (event: React.ChangeEvent<HTMLInputElement>) {
        const descriptor = event.currentTarget.value;

        let owner: string;
        let name: string;
        try {
            ({owner, name} = parseDescriptor(descriptor));
        } catch (e) {
            if (e instanceof ValidationError) {
                setValidation({state: "error", message: e.message});
            } else {
                console.error(
                    "Got unexpected error parsing descriptor",
                    descriptor,
                    e,
                );
                setValidation({
                    state: "error",
                    message: "Unexpected error validating repo.",
                });
            }
            return;
        }

        setValidation({state: "idle"});
        lockIdRef.current += 1;
        debouncedValidate(lockIdRef.current, owner, name);
    };

    return (
        <div className={classNames(props.className, "relative")}>
            <input
                id="searchBar"
                className="w-full border rounded-lg h-8 px-4 drop-shadow-md"
                spellCheck="false"
                enterKeyHint="search"
                onInput={handleInput}
            ></input>
            <div className="absolute right-2 top-0 bottom-0 flex items-center">
                {validation.state === "pending" && (
                    <SpinnerIcon className="animate-spin" />
                )}
                {validation.state === "error" && <ErrorIcon />}
                {validation.state === "ok" && <OkIcon />}
            </div>
        </div>
    );
}
