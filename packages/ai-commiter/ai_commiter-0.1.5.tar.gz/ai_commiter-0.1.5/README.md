# AI-Commiter

AI-powered Git commit message generator with multi-language support. Analyzes file changes and generates clear, structured commit messages using OpenAI API.

인공지능을 활용한 다국어 지원 Git 커밋 메시지 생성기입니다. 파일 변경 내역을 분석하고 OpenAI API를 통해 명확하고 구조화된 커밋 메시지를 생성합니다.

[![PyPI version](https://badge.fury.io/py/ai-commiter.svg)](https://badge.fury.io/py/ai-commiter)

## Key Features / 주요 기능

- **🌍 Multi-language Support / 다국어 지원**: Generate commit messages in Korean, English, Japanese, Chinese (Simplified/Traditional)
- **🤖 Intelligent Commit Message Generation / 지능형 커밋 메시지 생성**: Analyzes Git diff to create specific, structured commit messages
- **📝 Enhanced Conventional Commits / 향상된 Conventional Commits**: Uses standardized format with structured body using bullet points
- **📁 File Categorization & Summary / 파일 분류 및 요약**: Categorizes multiple file changes and provides summary information
- **⚙️ Custom Prompts / 커스텀 프롬프트**: Support for user-defined prompt templates
- **⚡ Simple CLI Command / 간단한 CLI 명령어**: Use `grpt` command for quick and convenient access
- **🧠 Multiple AI Models / 다양한 모델 지원**: Choose from various OpenAI GPT models with automatic complexity-based selection
- **📋 Structured Output / 구조화된 출력**: Body messages formatted with bullet points for better readability

## 설치 방법

### pipx로 설치 (권장)

[pipx](https://pypa.github.io/pipx/)는 애플리케이션을 격리된 환경에 설치하여 의존성 충돌 없이 사용할 수 있게 해줍니다.

```bash
# 1. pipx 설치 (처음 사용시)
pip install pipx
pipx ensurepath

# 2. 환경 변수 적용 (하나를 선택)
# macOS 사용자 (기본 zsh)
source ~/.zshrc
# Linux 또는 기타 bash 사용자
source ~/.bashrc

# 3. ai-commiter 설치
pipx install ai-commiter

# 4. API 키 설정

AI-Commiter는 두 가지 환경 변수를 통해 OpenAI API 키를 제공할 수 있습니다:

1. `AI_COMMITER_API_KEY`: AI-Commiter 전용 (권장)
2. `OPENAI_API_KEY`: 표준 OpenAI 환경 변수 (다른 OpenAI 애플리케이션과 공유)

프로그램은 먼저 `AI_COMMITER_API_KEY`를 확인하고, 없으면 `OPENAI_API_KEY`를 사용합니다.

## 일회성 설정 (현재 세션만 유효)
```bash
# macOS/Linux
export AI_COMMITER_API_KEY=your-api-key-here

# Windows
set AI_COMMITER_API_KEY=your-api-key-here
```

## 영구적 설정 (권장)
```bash
# macOS - zsh 사용자 (기본)
echo 'export AI_COMMITER_API_KEY=your-api-key-here' >> ~/.zshrc
source ~/.zshrc

# Linux/macOS - bash 사용자
echo 'export AI_COMMITER_API_KEY=your-api-key-here' >> ~/.bashrc
source ~/.bashrc

# Windows
setx AI_COMMITER_API_KEY "your-api-key-here"
# 위 명령 실행 후 터미널 재시작 필요
```

> **참고**: 기존에 `OPENAI_API_KEY`를 사용 중이라면 그대로 사용해도 됩니다.
```

> **문제해결**: 설치 후 `ai-commit` 명령어를 찾을 수 없는 경우:
> 1. `pipx ensurepath` 실행
> 2. `source ~/.zshrc` (macOS) 또는 `source ~/.bashrc` (Linux) 실행
> 3. 새로운 터미널을 열어 시도

### pip로 설치

```bash
pip install ai-commiter

# OpenAI API 키 설정
export OPENAI_API_KEY=your-api-key-here
# Windows에서는
# set OPENAI_API_KEY=your-api-key-here
```

## 업그레이드

새 버전이 출시되면 다음 명령어를 사용하여 업그레이드할 수 있습니다:

### pipx로 설치한 경우

```bash
pipx upgrade ai-commiter
```

### pip로 설치한 경우

```bash
pip install --upgrade ai-commiter
```

현재 설치된 버전을 확인하려면:

```bash
grpt --version
```

### 저장소에서 직접 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/ai-commiter.git
cd ai-commiter

# 패키지로 설치
pip install -e .

# OpenAI API 키 설정
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 사용 방법

### 기본 사용법

```bash
# 스테이지된 변경 사항에 대한 커밋 메시지 생성
grpt

# 생성된 메시지로 바로 커밋
grpt --commit

# 버전 확인
grpt --version

# 패키지 설치 없이 직접 실행할 경우
python -m ai_commiter.git_commit_ai
```

### 출력 예시 / Output Example

```
🧠 Complexity analysis: Simple changes (score: 0)
   • 1 files (+0), 39 diff lines (+0)
   → Selected gpt-3.5-turbo model
🤖 AI is generating commit message...

📝 Generated commit message:
--------------------------------------------------
docs: Update commit prompt template

- 커밋 프롬프트 템플릿 업데이트
- 커밋 메시지 템플릿 내용 수정 및 명확하게 작성 요청
--------------------------------------------------
```

### Additional Options / 추가 옵션

```bash
# Multi-language support / 다국어 지원
grpt --lang ko               # Korean / 한국어
grpt --lang en               # English / 영어
grpt --lang ja               # Japanese / 일본어
grpt --lang zh-CN            # Chinese Simplified / 중국어 간체
grpt --lang zh-TW            # Chinese Traditional / 중국어 번체

# Specify repository path / 특정 저장소 경로 지정
grpt --repo /path/to/repo --model gpt-4 --commit

# Disable file categorization / 파일 분류 기능 비활성화
grpt --no-categorize

# Include all unstaged changes / 스테이지되지 않은 모든 변경 사항 포함
grpt --all

# Use different OpenAI model / 다른 OpenAI 모델 사용
grpt --model gpt-4           # For complex changes
grpt --model gpt-3.5-turbo   # For simple changes (default)

# Use custom prompt template / 커스텀 프롬프트 템플릿 사용
grpt --prompt my_custom_prompt.txt

# Combined examples / 조합 예시
grpt --lang en --model gpt-4 --commit
grpt --lang ko --no-categorize
```

## Supported Languages / 지원 언어

| Language | Code | Locale | Example |
|----------|------|--------|---------|
| Korean / 한국어 | `ko`, `ko-KR` | ko-KR | `grpt --lang ko` |
| English / 영어 | `en`, `en-US`, `en-GB` | en-US, en-GB | `grpt --lang en` |
| Japanese / 일본어 | `ja`, `ja-JP` | ja-JP | `grpt --lang ja` |
| Chinese Simplified / 중국어 간체 | `zh`, `zh-CN` | zh-CN | `grpt --lang zh-CN` |
| Chinese Traditional / 중국어 번체 | `zh-TW` | zh-TW | `grpt --lang zh-TW` |

**Note**: Commit message titles are always generated in English (imperative mood) following Conventional Commits standard, while detailed descriptions are localized to the selected language.

## What's New / 새로운 기능

### Enhanced Commit Message Format / 향상된 커밋 메시지 형식

- **Structured Body**: Body messages now use bullet points (-) for better readability
- **Specific Descriptions**: AI avoids generic phrases like "update file" and provides concrete change descriptions
- **Improved Categorization**: Better commit type classification (docs, style, feat, etc.)

### Simple CLI Interface / 간단한 CLI 인터페이스

- **`grpt`**: Short, memorable command name for quick and convenient usage
- Easy to remember and type for frequent Git operations
- Consistent command interface across all features

### Enhanced Prompt System / 향상된 프롬프트 시스템

- More specific instructions for AI to generate concrete commit messages
- Mandatory formatting rules for consistent output
- Better examples and guidelines for commit types

## Custom Prompt Templates / 커스텀 프롬프트 템플릿

You can create custom prompt template files to adjust the style and format of AI-generated commit messages. Templates can use `{diff}`, `{language_instruction}`, and categorization variables.

커스텀 프롬프트 템플릿 파일을 만들어 AI가 생성하는 커밋 메시지의 스타일과 형식을 조정할 수 있습니다.

Example template / 예시 템플릿:

```
You are an expert Git commit message generator. Analyze the provided diff and create a high-quality commit message following these guidelines:

## Commit Format Requirements:
- Use Conventional Commits format: type(scope): description
- Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build
- Title: English imperative mood (max 50 chars)
- Body: Each line starts with "-" and describes specific changes

## Analysis Guidelines:
- Identify the main purpose of changes
- Avoid generic phrases like "update file" or "fix bug"
- Be specific about what was changed and why
- Group related changes logically

## Code Changes:
{diff}

## Output Requirements:
{language_instruction}

## Example Output:
feat: Add user authentication system

- Implement JWT-based login/logout functionality
- Add password hashing with bcrypt
- Create user session management
- Add authentication middleware for protected routes
```

## 요구 사항

- Python 3.7 이상
- Git
- OpenAI API 키

## 라이센스

MIT

