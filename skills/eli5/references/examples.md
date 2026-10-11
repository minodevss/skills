# Examples

Contents: 1. Failure modes · 2. A full explanation in English · 3. A full explanation in Korean · 4. Code · 5. A decision

## 1. Failure modes

Each pair shows the failure, then a fix.

Condescension

> Bad: Don't worry, this is super easy! Imagine a huuuge box of crayons...
>
> Good: An index is a sorted lookup list the database keeps, so it can jump straight to the matching rows, like the index at the back of a textbook.

Analogy carried too far

> Bad: Electricity is water in pipes, so a cut wire leaks electricity.
>
> Good: Water in pipes helps with one idea: more push gives more flow. It breaks down here: a cut wire does not leak. The current stops because the loop is broken.

Cute but wrong

> Bad: Air over the wing has to race to catch up with the air underneath.
>
> Good: The wing turns air downward, and pushing air down pushes the wing up. Air over the top does move faster, but not because it has to catch up.

Simplified into a false statement

> Bad: Git saves your changes in each commit.
>
> Good: Each commit records a snapshot of the whole project. Git reuses files that did not change, so snapshots are cheap. The "changes" you see are the difference between two snapshots.

A wall of analogies

> Bad: An API is like a waiter, and also like a menu, a power outlet, and a contract.
>
> Good: An API is like a restaurant menu with a kitchen behind it: you choose from a fixed list, and you never walk into the kitchen. It breaks down in one way: a menu does not refuse your order for coming too often, and many APIs do.

Burying the answer

> Bad: To understand this, we first need the history of HTTP...
>
> Good: The page is slow because each image is fetched one at a time. Here is why that happens.

Jargon as the explanation

> Bad: The query does a full table scan instead of using the B-tree.
>
> Good: The database reads every row to find yours (a "full table scan") instead of jumping to it with an index.

False precision

> Bad: This makes it 37.4% faster.
>
> Good: It was roughly two to three times faster in one test on 10,000 rows. The gain depends on the size of the data.

Accepting a false premise

> Bad: Macs get no viruses because Unix is secure.
>
> Good: Macs do get malware. Less of it targets them, mostly because attackers aim at the larger number of Windows machines.

Widening the claim

> Bad: A study shows coffee prevents heart disease.
>
> Good: In one observational study, coffee drinkers had somewhat lower rates of heart disease. A study of that kind cannot show that coffee causes the difference.

Korean: baby talk to an adult

> 나쁜 예: 친구야, 서버는 컴퓨터 친구들이 사는 집이란다!
>
> 좋은 예: 서버는 다른 컴퓨터의 요청을 받아 답을 돌려주는 컴퓨터예요. 우리가 앱을 열면 앱이 서버에 필요한 정보를 달라고 요청하고, 서버가 그 정보를 보내 줘요.

Korean: an unexplained loanword

> 나쁜 예: 레이턴시가 높아서 UX가 안 좋아요.
>
> 좋은 예: 버튼을 누르고 화면이 바뀌기까지 걸리는 시간(레이턴시)이 길어서, 쓰는 사람이 답답하게 느껴요.

## 2. A full explanation in English

Question: "ELI5: what is DNS?"

> DNS is the system that turns a website name like example.com into the number address computers actually use to find each other.
>
> Computers on the internet find each other by numeric addresses (IP addresses), much like houses are found by street addresses. People remember names better than numbers, so when you type example.com, your computer first asks a DNS server, "What is the address for example.com?" The server answers with a number such as 203.0.113.10, and your browser connects to that address. Your computer keeps the answer for a while, so the next visit skips the question.
>
> This skips who runs DNS servers and how they pass questions to each other. Want that part next?

What makes it work: the answer comes first, one concrete trace (typing a name, asking, connecting), the real term appears once in parentheses, the caching detail is included because it explains a common experience, and the omission is named.

## 3. A full explanation in Korean

질문: "쿠버네티스가 뭔지 비전공자도 알게 설명해 줘"

> 쿠버네티스는 여러 대의 서버에 프로그램을 나눠 실행하고, 하나가 멈추면 알아서 다시 띄워 주는 관리 프로그램이에요.
>
> 큰 서비스는 같은 프로그램을 수십 개 복사해서 여러 서버에서 동시에 돌려요. 사람이 하나하나 켜고 끄기엔 너무 많아서, "이 프로그램을 항상 5개 돌려 줘" 하고 목표만 적어 두면 쿠버네티스가 그 상태를 유지해 줘요. 서버 한 대가 고장 나서 프로그램이 3개로 줄면, 다른 서버에 2개를 새로 띄워 다시 5개로 맞춰요.
>
> 물류 센터 관리자에 비유할 수 있어요. 창고(서버)마다 짐(프로그램)을 나눠 두고, 창고 하나가 닫히면 짐을 다른 창고로 옮겨요. 다만 실제 쿠버네티스는 짐을 옮기는 게 아니라 다른 서버에서 새로 띄우는 거라, 멈춘 프로그램이 들고 있던 기록은 따로 저장해 두지 않으면 사라져요.
>
> 설정 파일을 어떻게 쓰는지는 뺐어요. 필요하면 이어서 설명할게요.

## 4. Code

Question: "Explain what this function does for our product manager."

```python
def should_retry(status, attempts):
    return status in (502, 503, 504) and attempts < 3
```

> This function decides whether the app tries a failed request again. It says yes only when the server answered with a "temporarily unavailable" kind of error and the app has tried fewer than 3 times. For example, if the payment server is briefly overloaded and answers 503 on the first try, the app tries again. If it still fails after 3 tries, the app stops and shows the error. Other errors, such as a wrong password, are never retried, because trying again would give the same answer.

## 5. A decision

Question: "Should we use a managed database or run our own? Explain it to the CEO."

> Use the managed database. It costs more per month but saves engineering time, and that time is our scarcer resource.
>
> Running our own is cheaper on the bill, roughly 40% in our own cost estimate, but one engineer would spend part of every week on backups, updates, and recovery. A managed service does that work for us, and its recovery is tested by the provider. The risk we accept is less control: if we later need a feature the provider does not offer, moving off it takes weeks.
