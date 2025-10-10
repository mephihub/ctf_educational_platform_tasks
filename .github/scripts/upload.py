import argparse
import requests
import yaml
from pathlib import Path
import glob


class MCTFapi:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

        self.session = requests.Session()
        self.session.cookies.set('api_key', self.api_key)

        status = self.__ping()
        if status != 200:
            print(f'Bad ping response - {status}')
            exit(1)

    def __do_get(self, endpoint):
        try:
            return self.session.get(f'{self.url}/api/v1/{endpoint}')
        except:
            print(f'Couldnt connect to {self.url}')
            exit(1)

    def __do_post(self, endpoint, data=None, files=None):
        try:
            return self.session.post(f'{self.url}/api/v1/{endpoint}', data=data, files=files)
        except:
            print(f'Couldnt connect to {self.url}')
            exit(1)

    def __ping(self):
        r = self.__do_get('')
        return r.status_code

    def update_course(self, name, description='', difficulty='', estimated_completion_time=0):
        data = {
            'name': name,
            'description': description,
            'difficulty': difficulty,
            'estimated_completion_time': estimated_completion_time,
        }

        return self.__do_post('courses/update', data=data)

    def update_task(self, course_name, task_name, answer, difficulty, info_path, writeup_path, description='', points=10):
        data = {
            'course_name': course_name,
            'name': task_name,
            'description': description,
            'answer': answer,
            'difficulty': difficulty,
            'points': points,
        }

        with open(info_path, 'rb') as info_file, open(writeup_path, 'rb') as writeup_file:
            files = {
                'info': ('info.md', info_file, 'text/markdown'),
                'writeup': ('writeup.md', writeup_file, 'text/markdown'),
            }
            return self.__do_post('tasks/update', data=data, files=files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        required=True,
    )
    parser.add_argument(
        '--api-key',
        required=True,
    )
    parser.add_argument(
        '--path',
        default='tasks',
    )

    args = parser.parse_args()

    tasks_path = Path(args.path)
    if not tasks_path.exists() or not tasks_path.is_dir():
        print("Tasks directory not found")
        return

    api = MCTFapi(args.url, args.api_key)

    courses = list(tasks_path.glob('*/*/topic.yml'))
    print(courses)

    for course_yml_path in courses:
        with open(course_yml_path, 'r') as f:
            course_yml = yaml.safe_load(f)
        course_name = course_yml['description']['name']

        print(f'Updating course {course_name}')
        api.update_course(
            course_name,
            description='No description provided',
            difficulty=course_yml['description']['difficulty'],
            estimated_completion_time=0
        )

        tasks = list(glob.glob(f'{str(course_yml_path).split('/topic.yml')[0]}/*/task.yml'))
        print(tasks)
        for task_path in tasks:
            with open(task_path, 'r') as f:
                task_yml = yaml.safe_load(f)

            print(f'Updating task {task_yml['description']['name']}')
            api.update_task(
                course_name, 
                task_yml['description']['name'], 
                task_yml['host-data']['flag'], 
                task_yml['description']['difficulty'],
                f'{task_path.split('/task.yml')[0]}/DESCRIPTION.md',
                f'{task_path.split('/task.yml')[0]}/solve/WRITEUP.md',
                'No description provided'
            )


if __name__ == '__main__':
    main()

