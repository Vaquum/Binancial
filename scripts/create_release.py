#!/usr/bin/env python3
"""Automated release creation script using Claude AI."""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import anthropic


def get_current_version() -> str:
    """Extract current version from pyproject.toml."""
    content = Path('pyproject.toml').read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError('Could not find version in pyproject.toml')
    return match.group(1)


def get_git_log_since_last_tag() -> str:
    """Get git log since the last tag, limited to prevent context overflow."""
    max_commits = 100
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            last_tag = result.stdout.strip()
            log_result = subprocess.run(
                ['git', 'log', f'{last_tag}..HEAD', '--oneline', '-n', str(max_commits)],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            log_result = subprocess.run(
                ['git', 'log', '--oneline', '-n', str(max_commits)],
                capture_output=True,
                text=True,
                check=True,
            )
    except subprocess.CalledProcessError as e:
        print(f'Error getting git log: {e}')
        return ''

    return log_result.stdout.strip()


def create_prompt() -> str:
    """Create the prompt for Claude to generate release information."""
    version = get_current_version()
    git_log = get_git_log_since_last_tag()
    current_date = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

    return f"""You are creating a new release for the Binancial project.

CURRENT STATE:
- Version in pyproject.toml: {version}
- Current date/time: {current_date}

GIT CHANGES SINCE LAST RELEASE:
{git_log}

TASK:
Based on the git changes above, create a JSON response with the following structure:
{{
    "version": "{version}",
    "tag": "v{version}",
    "release_name": "<creative name based on lunar calendar animals>",
    "release_notes": "<markdown formatted release notes with Summary and Details sections>"
}}

IMPORTANT REQUIREMENTS:
1. The tag MUST use lowercase 'v' prefix (e.g., v{version})
2. The release_name should be a creative play on lunar calendar animals (year, month, day, hour)
3. The release_notes must include:
   - ## Summary section: concise bullet points of key changes
   - ## Details section: beautiful essay-style comprehensive description
4. Analyze the git log carefully to understand what changed
5. Return ONLY valid JSON, no other text

Generate the release information now:"""


def parse_claude_response(response_text: str) -> dict:
    """Parse Claude's JSON response."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    start = response_text.find('{')
    if start == -1:
        raise ValueError(f'Could not find JSON in response: {response_text}') from None

    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(start, len(response_text)):
        char = response_text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = response_text[start : i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            f'Invalid JSON extracted: {json_str}'
                        ) from e

    raise ValueError(
        f'Could not find complete JSON object in response: {response_text}'
    ) from None


def tag_exists(tag: str) -> bool:
    """Check if a git tag already exists locally or remotely."""
    try:
        result = subprocess.run(
            ['git', 'tag', '-l', tag],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.stdout.strip() == tag:
            return True

        result = subprocess.run(
            ['git', 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}'],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        return len(result.stdout.strip()) > 0
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f'Warning: Could not check if tag exists: {e}')
        return False


def create_git_tag(tag: str, message: str) -> None:
    """Create and push a git tag."""
    subprocess.run(['git', 'tag', '-a', tag, '-m', message], check=True)
    subprocess.run(['git', 'push', 'origin', tag], check=True)
    print(f'Created and pushed tag: {tag}')


def create_github_release(tag: str, title: str, notes: str) -> None:
    """Create a GitHub release using gh CLI."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        notes_file = f.name
        f.write(notes)

    try:
        subprocess.run(
            [
                'gh',
                'release',
                'create',
                tag,
                '--title',
                title,
                '--notes-file',
                notes_file,
            ],
            check=True,
        )
        print(f'Created GitHub release: {title} ({tag})')
    finally:
        Path(notes_file).unlink(missing_ok=True)


def main() -> None:
    """Main function to orchestrate the release creation."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY environment variable not set')
        sys.exit(1)

    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print('Error: GITHUB_TOKEN environment variable not set')
        sys.exit(1)

    model = os.getenv('ANTHROPIC_MODEL', 'claude-opus-4-6')
    print(f'Using model: {model}')
    print('Creating release with Claude AI...')

    prompt = create_prompt()
    print(f'\nPrompt length: {len(prompt)} characters')

    client = anthropic.Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{'role': 'user', 'content': prompt}],
        )

        response_text = message.content[0].text
        print(f'\nClaude response received ({len(response_text)} characters)')

        release_info = parse_claude_response(response_text)

        print('\nRelease Information:')
        print(f'  Version: {release_info["version"]}')
        print(f'  Tag: {release_info["tag"]}')
        print(f'  Name: {release_info["release_name"]}')
        print('\nRelease Notes Preview:')
        print(release_info['release_notes'][:500] + '...')

        if tag_exists(release_info['tag']):
            print(
                f'\nTag {release_info["tag"]} already exists. '
                'Skipping release creation.'
            )
            print(
                'This is expected when the version in pyproject.toml '
                'has not changed.'
            )
            sys.exit(0)

        create_git_tag(
            release_info['tag'],
            f'Release {release_info["version"]}: {release_info["release_name"]}',
        )

        create_github_release(
            release_info['tag'],
            release_info['release_name'],
            release_info['release_notes'],
        )

        print('\nRelease created successfully!')

    except Exception as e:
        print(f'\nError creating release: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
