

from requests import Response, patch
from .exceptions import GradebookColumnNotFoundError
from bbpy.logger_client import Logger


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_client import BBUser
    from .blackboard_client import BlackboardClient



# def convert_to_iso8601(date_str, time_str):
#     # Combine date and time strings into a single string
#     date_string = f"{date_str} {time_str}"

#     # Parse the date string into a datetime object
#     date_obj = datetime.strptime(date_string, '%m-%d-%Y %I:%M %p')

#     # Assuming the datetime is in local time (US/Eastern), handle DST correctly
#     local_tz = pytz.timezone('US/Central')

#     # Localize the datetime object to the US/Eastern time zone, accounting for DST
#     local_time = local_tz.localize(date_obj, is_dst=None)  

#     # Convert the local time to UTC
#     utc_time = local_time.astimezone(pytz.utc)

#     # Format the datetime in ISO 8601 format with no seconds or milliseconds
#     iso8601_format = utc_time.strftime('%Y-%m-%dT%H:%M:00Z')

#     return iso8601_format


# def convert_from_iso8601(iso8601_str):
#     # Try to parse the ISO 8601 string with milliseconds first
#     try:
#         utc_time = datetime.strptime(iso8601_str, '%Y-%m-%dT%H:%M:%S.%fZ')
#     except ValueError:
#         # If it fails, parse it without milliseconds
#         utc_time = datetime.strptime(iso8601_str, '%Y-%m-%dT%H:%M:%SZ')

#     # Set the timezone to UTC
#     utc_time = pytz.utc.localize(utc_time)

#     # Convert to local time (US/Central)
#     local_tz = pytz.timezone('US/Central')
#     local_time = utc_time.astimezone(local_tz)

#     # Format the local time as "3-12-2025 2:00 PM"
#     local_time_str = local_time.strftime('%m-%d-%Y %I:%M %p')

#     return local_time_str


class GradebookClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    def update_grade(self, course_id: str, column_id: str, username: str, new_value: str) -> None:
        """Updates a grade in a specific column (only handles text right now)

        Args:
            course_id (str): _description_
            column_id (str): _description_
            user_id (str): The student in the course to update grade
            new_value (str): _description_
        """

        # Get column data for logs
        col_name = ""

        # User is made to get the name, for the logs
        user: BBUser = self.parent.user.get_user_object(username)

        url = self.parent.endpoints.get_column(course_id, column_id)

       # _get_column_data = f"{ORG_DOMAIN}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns/{column_id}"

        response2 = self.parent.get(url)

        # response2 = get(url, headers={
        # 'Authorization': 'Bearer ' + get_access_token(),
        # 'Content-Type': 'application/json'
        # })
        #print(response2.text)

        if response2.status_code == 200:
            data = response2.json()
            col_name = data["name"]
        else:
            raise GradebookColumnNotFoundError()


        _data = {
        "text": f"{new_value}",
        #"score": 0,
        #"notes": "string",
        #"feedback": "string",
        #"exempt": false,
        }


    

        #_update_grade = f"{ORG_DOMAIN}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns/{column_id}/users/userName:{username}"
     

        _update_grade = self.parent.endpoints.update_grade(course_id, column_id, username)



        # response: Response = patch(_update_grade, headers={
        # 'Authorization': 'Bearer ' + get_access_token(),
        # 'Content-Type': 'application/json'
        # }, json=_data)

        response = self.parent.patch(url=_update_grade, json=_data)

        #print(response.text)


        if response.status_code == 200:
            ##data = res_user_data.json()
            Logger.info(msg=f"{col_name} for {user.first_name} {user.last_name} was updated to: {new_value}")
            #print(f"{col_name} for {user.first_name} {user.last_name} was updated to: {new_value}")
        else:
            try:
                error_message = response.json().get('message')  # Assuming error details are in JSON format
            except ValueError:
                error_message = response.text  # Fallback to plain text response if JSON parsing fails
        
            Logger.error(msg=f"Failed to update {col_name} for {user.first_name} {user.last_name}. Error: {error_message}")

    #TODO: Test to make sure date format works
    def update_column_due_date(course_id: str, column_id: str, due_date: str): # column_id: str, new_date: str) -> None:

        _data = {
            "grading": {
                "due": f"{due_date}"
            }
        }

        if due_date == "":
            _data = {
                "grading": {
                    "due": None
                }
            }  

        _update_grade = f"{"ORG_DOMAIN"}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns/{column_id}"
    
        response: Response = patch(_update_grade, headers={
            'Authorization': 'Bearer ' + "get_access_token()",
            'Content-Type': 'application/json'
        }, json=_data)

        #print(response.text)

        if response.status_code == 200:
            ##data = res_user_data.json()

           # print(f"Assignment: {col.name} due date has been set to {convert_from_iso8601(col.due_date)}")
           pass
        else:
            try:
                error_message = response.json().get('message')  # Assuming error details are in JSON format
            except ValueError:
                error_message = response.text  # Fallback to plain text response if JSON parsing fails
        
            print(error_message)

    #FIXME: Works in old way, update to package
    def create_gradebook_column(
        self, course_id: str, column_name: str, description: str, score: int
    ) -> None:
        data = {
            # "externalId": "string",
            # "dataSourceId": "string",
            "name": f"{column_name}",
            # "displayName": f"{column_name}",
            "description": f"{description}",
            # "termId": "",
            # "closedComplete": true,
            # "termId": "string",
            "score": {"possible": score},
            "availability": {
                "available": "Yes",
            },
        }

        #make_col = f"{ORG_DOMAIN}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns"

        make_col = self.parent.endpoints.create_column(course_id)

        # response = post(
        #     make_col,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        #     json=_data,
        # )

        response = self.parent.post(make_col, data)

        # TODO: Add other possible response codes

        if response.status_code == 201:
            ##data = res_user_data.json()
            print(f"Column {column_name} has been made in course {course_id}")
            Logger.info(f"Column {column_name} has been made in course {course_id}")

        if response.status_code == 400:
            try:
                error = response.json()
                print("Status:", error.get("status"))
                print("Code:", error.get("code"))
                print("Message:", error.get("message"))
                print("Developer Message:", error.get("developerMessage"))
                print("Extra Info:", error.get("extraInfo"))
            except ValueError:
                print("400 error but response is not JSON:", response.text)

        else:
            Logger.error(response.text)



