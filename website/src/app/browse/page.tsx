import Link from "next/link";
import {FaGithub as GitHubIcon} from "react-icons/fa";
import RepoSearch from "./RepoSearch";

export default function Home() {
    return (
        <main className="flex min-h-screen flex-col items-center p-8 lg:p-16">
            <div className="flex flex-col lg:flex-row w-full max-w-5xl items-center justify-between text-sm font-mono gap-4">
                <div className="flex items-center gap-2 items-end justify-center text-2xl font-semibold">
                    pre-commit-hub
                    <a href="https://github.com/itsjohncs/pre-commit-hub">
                        <GitHubIcon className="text-gray-700 hover:text-inherit" />
                    </a>
                </div>
                <p className="flex flex-wrap justify-center border border-gray-300 rounded-xl bg-gray-200 p-4 dark:bg-zinc-800/30">
                    Install locally with&nbsp;
                    <code className="font-bold">
                        pip install pre-commit-hub
                    </code>
                </p>
            </div>
            <div className="flex items-center flex-col gap-2 w-full text-md max-w-5xl mt-16 lg:mt-36">
                <label
                    className="text-center font-semibold"
                    htmlFor="searchBar"
                >
                    Add GitHub repository
                </label>
                <RepoSearch className="w-full md:w-2/3" />
                <p>
                    The respository must contain a valid{" "}
                    <code>.pre-commit-hooks.yaml</code> file in its root
                    directory.
                </p>
            </div>
        </main>
    );
}
