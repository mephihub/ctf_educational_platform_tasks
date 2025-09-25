# jeopardy_ctf_template
[![check-tasks](https://github.com/dtlhub/ctf_educational_platform/actions/workflows/check-tasks.yml/badge.svg?branch=master&event=push)](https://github.com/dtlhub/ctf_educational_platform/actions/workflows/check-tasks.yml)

Development workflow:

1. Create branch named `$TASK`.
2. Write your code in `tasks/$CATEGORY/$TOPIC/$TASK`
3. Validate your task with `TASK=$TASK ./check.py validate`. 
4. Up your task with `TASK=$TASK ./check.py up`. 
5. Check your task with `./check.py validate`. 

task.yml:

