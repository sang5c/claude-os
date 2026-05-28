---
name: git-push
description: 이 저장소의 커밋을 sang5c 계정으로 원격(origin)에 push한다. 사용자가 "푸시해줘", "push", "git push", "원격에 올려줘" 같이 요청할 때 사용한다.
---

# git-push

이 저장소는 **항상 sang5c 계정**으로만 원격 작업을 한다. 전역 gh 활성 계정을 바꾸지 않고, 저장소 로컬 설정으로 sang5c 토큰을 런타임에 가져와 인증한다. (다른 저장소에는 영향 없음)

## Workflow

1. **sang5c 인증 설정 점검** — push 전에 로컬 credential 설정이 살아있는지 확인한다.
   ```bash
   git config --local credential.https://github.com.helper
   ```
   출력에 `gh auth token --user sang5c`가 포함돼 있어야 한다. 없으면 아래 "설정 복구"로 다시 잡는다.

2. **현재 상태 파악** — 병렬로 실행한다.
   - `git status -sb` (현재 브랜치, 추적/미푸시 상태)
   - `git log @{u}.. --oneline` (업스트림 대비 푸시될 커밋; 업스트림 없으면 `git log --oneline -10`)
   - `git remote -v`

3. **사용자 확인** — push될 브랜치/커밋과 대상 원격을 보여주고 확인을 받는다. push는 공유 상태를 바꾸는 작업이므로 항상 확인한다.

4. **push 실행**
   - 업스트림이 있으면: `git push`
   - 없으면: `git push -u origin <branch>`
   - force push는 사용자가 명시적으로 요청하지 않으면 절대 하지 않는다. main/master로의 force push는 요청받아도 경고한다.

5. **검증** — `git status -sb`로 `origin/<branch>`와 동기화됐는지 확인하고, 커밋 작성자가 `sang5c`인지 `git log -1 --format='%an <%ae>'`로 확인한다.

## 설정 복구

로컬 sang5c 인증이 빠져 있으면 다음으로 복구한다.

```bash
git config --local credential.helper ""
git config --local credential.https://github.com.helper '!f() { test "$1" = get && echo "username=sang5c" && echo "password=$(gh auth token --user sang5c)"; }; f'
```

## 주의

- 전역 `gh auth switch`로 계정을 바꾸지 않는다 (다른 저장소에 영향). 반드시 저장소 로컬 설정으로만 처리한다.
- `gh auth token --user sang5c`가 실패하면 `sang5c` 계정 로그인이 풀린 것이므로, `gh auth login`으로 sang5c 재로그인을 안내한다.
