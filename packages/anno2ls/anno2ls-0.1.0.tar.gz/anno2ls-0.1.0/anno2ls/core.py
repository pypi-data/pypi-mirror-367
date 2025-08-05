import requests
import os
import pprint
import json
import base64

def delete_task(task_id, url, headers):
    url = f"{url}/api/tasks/{task_id}"
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Deleted task ID: {task_id}")
    else:
        print(f"Failed to delete task ID: {task_id}: {response.text}")

def convert_labelme(points, width, height):
    return [[(x / width) * 100, (y / height) * 100] for x, y in points]

class Anno2LS:
    def __init__(self, token: str, url: str):
        self.token = token
        self.url = url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {self.token}"
        }

    def get_init(self):
        return self.token, self.url, self.headers
        
    def get_all_filenames(self, project_id: int):
        try:
            filenames = []
            page = 1
            while True:
                url = f"{self.url}/api/projects/{project_id}/tasks?page={page}&page_size=100"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    #print(f"Failed to fetch tasks or all pages already fetched. Response: {response.text}")
                    break
    
                page_tasks = response.json()
                if not page_tasks:
                    break
    
                for task in page_tasks:
                    data = task.get("data", {})
                    filename = data.get("image") or data.get("filename") or data.get("file")
                    if filename:
                        filenames.append(filename)
    
                page += 1
            return filenames
        except Exception as e:
            print(f"Error: {e}")

    def get_all_tasks(self, project_id: int):
        try:
            tasks = []
            page = 1
            while True:
                url = f"{self.url}/api/projects/{project_id}/tasks?page={page}&page_size=100"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    #print(f"Failed to fetch tasks or all pages already fetched. Response: {response.text}")
                    break
                    
                page_tasks = response.json()
                if not page_tasks:
                    break
                tasks.extend(page_tasks)
                page += 1
    
            return tasks
        except Exception as e:
            print(f"Error: {e}")

    def delete_empty_task(self, project_id: int):
        tasks = self.get_all_tasks(project_id)
        for task in tasks:
            try:
                task_id = task['id']
                if not task.get("annotations"):
                    delete_task(task_id, self.url, self.headers) 
            except Exception as e:
                print(f"Failed to delete task {task.get('id', 'unknown')}: {e}")

    def delete_all_task(self, project_id: int):
        tasks = self.get_all_tasks(project_id)
        for task in tasks:
            try:
                task_id = task['id']
                delete_task(task_id, self.url, self.headers) 
            except Exception as e:
                print(f"Failed to delete task {task.get('id', 'unknown')}: {e}")

    def import_images(self, image_path: str, project_id: int):
        try:
            if not os.path.isdir(image_path):
                print(f"Path {image_path} does not exist or is not a directory.")
                return
                
            image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
            for file in image_files:
                full_path = os.path.join(image_path, file)
                with open(full_path, "rb") as f:
                    response = requests.post(
                        f"{self.url}/api/projects/{project_id}/import",
                        headers=self.headers,
                        files={"file": f}
                    )
    
                if response.status_code == 201:
                    print(f"Uploaded: {file}")
                else:
                    print(f"Failed to upload {file}: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error: {e}")


    def import_preannotated(self, annotation_path: str, project_id: int, annotation_type: str = "labelme"):
        filenames = self.get_all_filenames(project_id)
        try:
            if annotation_type == "labelme":
                path_anno = annotation_path
                hold_import = []
                for image_name in filenames:
                    import_data = {}
                    import_data['data'] = {'image': image_name}
                    import_data['annotations'] = [{'result': []}]
                
                    json_path = os.path.join(path_anno, image_name.split('-', 1)[-1].rsplit('.')[0]+'.json')
                    json_data = json.load(open(json_path))
    
                    for anno_data in json_data['shapes']:
                        import_data["annotations"][0]["result"].append(
                            {
                                "from_name": "label",
                                "to_name": "image",
                                "type": "polygonlabels",
                                "original_width": json_data['imageWidth'],
                                "original_height": json_data['imageHeight'],
                                "image_rotation": 0,
                                "value": {
                                    "points": convert_labelme(anno_data['points'], json_data['imageWidth'], json_data['imageHeight']),
                                    "polygonlabels": [anno_data['label']]
                                }
                            }
                        )
                    hold_import.append(import_data)
    
    
            upload_url = f"{self.url}/api/projects/{project_id}/import"
            response = requests.post(
                upload_url,
                headers=self.headers,
                json=hold_import 
            )
            
            if response.status_code == 201:
                print("Import successful.")
            else:
                print(f"Failed to import. Status code: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Error: {e}")
            