"""
This module provides functions for managing courses in an blackboard.

Functions in this module allow you to create, delete, and update course information,
as well as query details about existing courses. The primary goal of this module
is to facilitate course management operations for the LMS administrators.

Author: sugarvoid

License: MIT
"""

import json
from time import sleep
from typing import TYPE_CHECKING

from .formatting import format_date
from bbpy.exceptions import BlackboardAPIError, CourseNotFoundError, UserNotFoundError

if TYPE_CHECKING:
    from .user_client import UserClient, BBUser
    from .blackboard_client import BlackboardClient #, get_access_token

class BBCourse:
    def __init__(
        self,
        course_id: str,
        name: str,
        created: str,
        last_updated: str,
        term: str,
        available: str,
    ) -> None:
        self.course_id = course_id
        self.name = name
        self.created = format_date(created)
        self.last_updated = format_date(last_updated)
        self.instructor: list
        #FIXME: I don't think this will work
        self.term = term
        self.is_available = available


class CourseClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    # Works. Tested 8/5/2025
    def add_child_course(self, course_id: str, child_id: str) -> None:
        url = self.parent.endpoints.add_child(course_id=course_id, child_id=child_id)
        res_add_child = self.parent.put(url=url)

        #TODO: Add exceptions, maybe
        if res_add_child.status_code != 201:
            self.parent.logger.error(f"Failed to add {child_id} to {course_id}")

        if res_add_child.status_code == 201:
            self.parent.logger.info(f"{child_id} has been added to {course_id}, as a child course")

    # Works. Tested 8/4/2025
    def enroll_user(self, username: str, course_id: str, role: str = "Student") -> None:
        if not self.parent.course.does_course_exist(course_id):
            raise CourseNotFoundError("Course does not exist")

        if self.parent.user.does_user_exist(username):
            #TODO: Used to get the user's name, but do the logs really need it?? 
            user: BBUser = self.parent.user.get_user_object(username=username)

            data = {
                "availability": {"available": "Yes"},
                "courseRoleId": role.strip(),
            }

            url = self.parent.endpoints.enroll_user(course_id.strip(), username.strip())
            res_user_data = self.parent.put(url=url, json=data)

            
            if res_user_data.status_code == 409:
                self.parent.logger.error(
                    f"{user.first_name} {user.last_name} ({username}) is in course {course_id} already"
                )

            if res_user_data.status_code == 201:
                self.parent.logger.info(
                    f"{user.first_name} {user.last_name} ({username}) has been added to {course_id}, as {role}"
                )

            if res_user_data.status_code == 400:
                self.parent.logger.error("Could not match roleId to any existing roles")

        else:
            self.parent.logger.error(
                f"Failed to enroll user {username} into {course_id}, the user was not found"
            )
            raise UserNotFoundError(f"User {username} was not found")
            

    def does_course_exist(self, course_id: str) -> bool:
        """Checks to see if a course is already added to the system
            with the provided course ID.

        Args:
            course_id (str): _description_

        Returns:
            bool: True if course is already in the system.
        """

        url = self.parent.endpoints.get_course(course_id=course_id)
        response = self.parent.get(url)

        if response.status_code == 404:
            return False
        elif response.status_code == 400:
            raise BlackboardAPIError("The request did not specify a valid courseId")
        elif response.status_code != 200:
            raise BlackboardAPIError(
                f"Unexpected response: {response.status_code} {response.text}"
            )
        return True

    def remove_user_from_course(self, username: str, course_id: str) -> None:
        """
        Remove the specified user from the given course in Blackboard.

        Args:
            client (BlackboardWrapper): Authenticated Blackboard client instance.
            username (str): The username of the user to remove.
            course_id (str): The course ID of the course.
        """

        if not self.parent.course.does_course_exist(course_id):
            raise Exception("Course does not exist")

        # Have to change membership to student first. Yes, we can check if the user is
        # already a student, but that would also cost an api call, so nothing is gained
        self.__update_course_membership(self, course_id, username, "Student")

        # TODO: rename
        _remove_user = f"{self.parent.api_base_url}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{username}"

        try:
            _response = self.parent.delete(_remove_user)
            if _response.status_code == 204:
                self.parent.logger.info(f"{username} was removed from {course_id}.")
            else:
                print(f"Failed to remove {username} from course. {_response.text}")
                self.parent.logger.error(
                    f"Failed to remove {username} from course. {_response.text}"
                )

        except Exception as e:
            self.parent.logger.error(f"An error occurred while checking user existence: {e}")

        # _response = delete(
        #     _remove_user,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        # if _response.status_code == 204:
        #     Logger.info(f"{username} was removed from {course_id}.")
        # else:
        #     print(f"Request failed, check logs. {Logger.get_file_path()}")
        #     Logger.error(f"Failed to remove {username} from course. {_response.text}")


    #TODO: FIX THIS!
    def remove_by_role(
        self, client: "BlackboardClient", course_id: str, role: str = ""
    ) -> None:
        """Remove all the users in a course by a specific role.

        Args:
            course_id (str): _description_
            role (str): _description_ ["Student", "Instructor"]
        """

        # TODO: Check that the role is a valid role in te list

        my_guys = self.get_users_in_course_by_role(course_id=course_id, role=role)

        if len(my_guys) > 0:
            for u in my_guys:
                _username = UserClient.get_local_username_from_id(
                    client=client, username=u.get("userId")
                )
                self.remove_user_from_course(_username, course_id=course_id)
                sleep(2)
        else:
            self.parent.logger.info(
                f"Attempt to remove users from {course_id}, but zero users were found."
            )


    #TODO: this could just point to the get_users_by_role and pass in "Student"??
    def get_course_student_list(self, course_id: str) -> list:
        """Makes a list of all the users in a course with student role.

        Args:
            course_id (str): _description_
        """
        _course_id = course_id.strip()
        my_guys = self.get_users_in_course_by_role(course_id=_course_id, role="Student")
        students: list = []

        for guy in my_guys:
            id = self.parent.user.get_local_username_from_id(user_id=guy.get("userId"))
            students.append(id)
        
        return students
 


    #TODO: Remove classic option
    def create_empty_course(
        self, course_id: str, course_name: str) -> None:
        """Creates an empty Ultra course. Used for when it will be a child course

        Args:
            course_id (str): The ID of the course.
            course_name (str): The name of the course.
        """

        _data = {
            "courseId": f"{course_id}",
            "name": f"{course_name}",
            # "description": "",
            # "termId": "",
            "organization": False,
            "ultraStatus": "Ultra",
            "allowGuests": False,
            "allowObservers": False,
            # "closedComplete": true,
            "availability": {
                "available": "No",
                "duration": {
                    "type": "Continuous",
                },
            },
            "enrollment": {
                "type": "InstructorLed",
            },
        }

        url = self.parent.endpoints.create_course()
        response = self.parent.post(url=url, json=_data)

        if response.status_code == 201:
            self.parent.logger.info(f"Empty course: {course_id} was created")

        else:
            self.parent.logger.error(response.text)


    # TODO: Double check this still works
    # TODO: Make forum choice an option in args
    def copy_course_exact(self, master_id: str, copy_id: str) -> None:
        if not self.does_course_exist(master_id):
            self.parent.logger.error(f"Course: {master_id} does not exist")
            return

        # TODO: Check to make sure "copy from" course even exist
        _data = {
            "targetCourse": {
                "courseId": f"{copy_id.strip()}",
                # "id": {}
            }
        }
        ### Using the payload without the "copy" object is equivalent to doing an exact copy of the course, which means all course settings will be replicated.
        # if forum_option in ("f", "fs"):
        #     _forums = ""
        #     if forum_option == "f":
        #         _forums = "ForumsOnly"
        #         Logger.info(f"Copying only the forums for course {copy_id}")
        #     elif forum_option == "fs":
        #         _forums = "ForumsAndStarterPosts"
        #         Logger.info(f"Copying the forums and starter post for course {copy_id}")

        #     _data["copy"] = {
        #         "adaptiveReleaseRules": True,
        #         "announcements": True,
        #         "assessments": True,
        #         "blogs": True,
        #         "calendar": True,
        #         "contacts": True,
        #         "contentAlignments": True,
        #         "contentAreas": True,
        #         "discussions": f"{_forums}",
        #         "glossary": True,
        #         "gradebook": True,
        #         "groupSettings": True,
        #         "journals": True,
        #         "retentionRules": True,
        #         "rubrics": True,
        #         "settings": {
        #             "availability": False,
        #             "bannerImage": True,
        #             "duration": True,
        #             "enrollmentOptions": True,
        #             "guestAccess": True,
        #             "languagePack": True,
        #             "navigationSettings": True,
        #             "observerAccess": True,
        #         },
        #         "tasks": True,
        #         "wikis": True,
        #     }
        # else:
        #     Logger.info(f"Copying all posts from the discussion board in course {copy_id.strip()}")

        copy_course = self.parent.endpoints.copy_course(course_id=master_id.strip())

        # response = post(
        #     copy_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        #     json=_data,
        # )

        response = self.parent.post(url=copy_course, json=_data)

        if response.status_code == 202:
            ##data = res_user_data.json()
            print(f"course: {copy_id} was created")
            self.parent.logger.info(f"course: {copy_id} was successfully created from: {master_id}")

        else:

            self.parent.logger.error(response.text)


    def copy_course_new(self, master_id: str, copy_id: str) -> None:
        if not self.does_course_exist(master_id):
            raise CourseNotFoundError(f"Course: {master_id} does not exist")
 
        _data = {
            "targetCourse": {
                "courseId": f"{copy_id.strip()}",
                # "id": {}
            }
        }
        ### Using the payload without the "copy" object is equivalent to doing an exact copy of the course, which means all course settings will be replicated.
        # if forum_option in ("f", "fs"):
        #     _forums = ""
        #     if forum_option == "f":
        #         _forums = "ForumsOnly"
        #         Logger.info(f"Copying only the forums for course {copy_id}")
        #     elif forum_option == "fs":
        #         _forums = "ForumsAndStarterPosts"
        #         Logger.info(f"Copying the forums and starter post for course {copy_id}")

        _data["copy"] = {
            "adaptiveReleaseRules": True,
            "announcements": True,
            "assessments": True,
            "blogs": True,
            "calendar": True,
            "contacts": True,
            "contentAlignments": True,
            "contentAreas": True,
            "discussions": "ForumsAndStarterPosts",
            #"discussions": "ForumsOnly",
            "glossary": True,
            "gradebook": True,
            "groupSettings": True,
            "journals": True,
            "retentionRules": True,
            "rubrics": True,
            "settings": {
                "availability": False,
                "bannerImage": True,
                "duration": True,
                "enrollmentOptions": True,
                "guestAccess": True,
                "languagePack": True,
                "navigationSettings": True,
                "observerAccess": True,
            },
            "tasks": True,
            "wikis": True,
        }
        # else:
        # Logger.info(f"Copying all posts from the discussion board in course {copy_id.strip()}")

        # copy_course = (
        #     f"{self.parent.api_base_url}/learn/api/public/v2/courses/courseId:{master_id.strip()}/copy"

        # )

        copy_course = self.parent.endpoints.copy_course(course_id=master_id)

        # response = post(
        #     copy_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        #     json=_data,
        # )

        response = self.parent.post(url=copy_course, json=_data)

        if response.status_code == 202:
            ##data = res_user_data.json()
            print(f"course: {copy_id} was created")
            self.parent.logger.info(f"course: {copy_id} was successfully created from: {master_id}")

        else:

            self.parent.logger.error(response.text)






    # # TODO: Make forum choice an option in args
    # def copy_course(self, master_id: str, copy_id: str) -> None:
    #     if not self.does_course_exist(master_id):
    #         raise CourseNotFoundError(f"Course: {master_id} does not exist")

    #     # TODO: Check to make sure "copy from" course even exist
    #     _data = {
    #         "targetCourse": {
    #             "courseId": f"{copy_id.strip()}",
    #             # "id": {}
    #         }
    #     }
    #     ### Using the payload without the "copy" object is equivalent to doing an exact copy of the course, which means all course settings will be replicated.
    #     # if forum_option in ("f", "fs"):
    #     #     _forums = ""
    #     #     if forum_option == "f":
    #     #         _forums = "ForumsOnly"
    #     #         Logger.info(f"Copying only the forums for course {copy_id}")
    #     #     elif forum_option == "fs":
    #     #         _forums = "ForumsAndStarterPosts"
    #     #         Logger.info(f"Copying the forums and starter post for course {copy_id}")

    #     #     _data["copy"] = {
    #     #         "adaptiveReleaseRules": True,
    #     #         "announcements": True,
    #     #         "assessments": True,
    #     #         "blogs": True,
    #     #         "calendar": True,
    #     #         "contacts": True,
    #     #         "contentAlignments": True,
    #     #         "contentAreas": True,
    #     #         "discussions": f"{_forums}",
    #     #         "glossary": True,
    #     #         "gradebook": True,
    #     #         "groupSettings": True,
    #     #         "journals": True,
    #     #         "retentionRules": True,
    #     #         "rubrics": True,
    #     #         "settings": {
    #     #             "availability": False,
    #     #             "bannerImage": True,
    #     #             "duration": True,
    #     #             "enrollmentOptions": True,
    #     #             "guestAccess": True,
    #     #             "languagePack": True,
    #     #             "navigationSettings": True,
    #     #             "observerAccess": True,
    #     #         },
    #     #         "tasks": True,
    #     #         "wikis": True,
    #     #     }
    #     # else:
    #     #     Logger.info(f"Copying all posts from the discussion board in course {copy_id.strip()}")

    #     copy_course = f"{self.parent.ORG_DOMAIN}/learn/api/public/v2/courses/courseId:{master_id.strip()}/copy"

    #     response = post(
    #         copy_course,
    #         headers={
    #             "Authorization": "Bearer " + get_access_token(),
    #             "Content-Type": "application/json",
    #         },
    #         json=_data,
    #     )

    #     if response.status_code == 202:
    #         ##data = res_user_data.json()
    #         ##print(f"course: {copy_id} was created")
    #         self.parent.logger.info(f"course: {copy_id} was successfully created from: {master_id}")

    #     else:

    #         #TODO: Make better error handling
    #         self.parent.logger.error(response.text)

    # This works. Been tested.
    def change_user_availability(
        self, student_id: str, course_id: str, available: str = "No"
    ):
        """Update a student's availability in a course 

        Args:
            student_id (str): _description_
            course_id (str): _description_
            available (str, optional): _description_. Defaults to "No".
        """

        if available not in ["Yes", "No"]:
            raise BlackboardAPIError(
                f'For available, you can only use either "Yes" or "No". You used: "{available}"...'
            )

        _data = {
            # "dataSourceId": "string",
            "availability": {"available": available},
        }

        #update_course = f"{self.parent.ORG_DOMAIN}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{student_id}"

        update_course = self.parent.endpoints.course_user(course_id, student_id)
        # response = patch(
        #     update_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        #     json=_data,
        # )

        response = self.parent.patch(update_course, _data)

        # if not response.ok:
        #   Logger.error(f'Failed to update availability. Status Code: {response.status_code}, Response: {response.text}')
        #  raise Exception(f'Failed to update availability. Status Code: {response.status_code}, Response: {response.text}')

        # TODO: Raise errors instead for better error handling
        match response.status_code:
            case 200:
                self.parent.logger.info(
                    f"{student_id} has been made available({available}) in course {course_id}"
                )
            case 400:
                self.parent.logger.error("The request did not specify valid data")
            case 404:
                self.parent.logger.error("Course not found or course membership not found")
            case 409:
                self.parent.logger.error("Conflict?? what does that even mean")


    def _update_course(self, course_id: str, data: dict, action: str = "updated") -> None:
        """(Internal) Helper method. Do not use directly."""
        url = self.parent.endpoints.get_course(course_id=course_id)
        response = self.parent.patch(url=url, json=data)

        if response.status_code == 200:
            self.parent.logger.info(f"Course {course_id} {action}.")
        else:
            self.parent.logger.error(
                f"Failed to update course {course_id}. Status: {response.status_code}. Response: {response.text}"
            )
            # Raise a real exception 

    # This works
    def update_course_title(self, course_id: str, new_name: str) -> None:
        self._update_course(course_id=course_id, data={"name": new_name}, action=f'renamed to "{new_name}"')

    #TODO: Test this
    #TODO: If works, add to user class
    def update_course_term_new(self, course_id: str, term_id: str) -> None:
        self._update_course(course_id=course_id, data={"termId": term_id.strip()}, action=f'term set to "{term_id.strip()}"')
    
    #TODO: Remove old version
    def update_course_data_source(self, course_id: str, data_source: str) -> None:
        self._update_course(course_id=course_id, data={"dataSourceId": data_source.strip()}, action=f'data source set to "{data_source.strip()}"')

    def update_course_availability(self, course_id: str, availability: str) -> None:
        if availability in ["Yes", "No", "Disabled"]:
            data = {
                "availability": {
                    "available": f"{availability}",
                },
            }
            self._update_course(course_id=course_id, data=data, action=f'set to "{availability}"')
        else:
            raise BlackboardAPIError(f"{availability} is not a valid option for setting course availability")


    def rename_course(self, course_id: str, new_name: str) -> None:
        _data = {"name": f"{new_name}"}
        url = self.parent.endpoints.get_course(course_id=course_id)

        response = self.parent.patch(url=url, json=_data)
        # TODO: Add real exceptions
        if response.status_code == 200:
            self.parent.logger.info(f"Course {course_id} has been renamed to {new_name}")
        else:
            self.parent.logger.error(f"Failed to rename {course_id}. {response.text}")
    
    def update_course_term(self, course_id: str, term_id: str) -> None:
        term_id = term_id.strip()
        _data = {"termId": f"{term_id}"}
        url = self.parent.endpoints.get_course(course_id=course_id)
        response = self.parent.patch(url=url, json=_data)
        # TODO: Add real exceptions
        if response.status_code == 200:
            self.parent.logger.info(f"Course {course_id} has termed changed to {term_id}")
        else:
            self.parent.logger.error(f"Failed to update term for {course_id}. {response.text}")


    # def update_course_post_copy(
    #     self,
    #     course_id: str,
    #     term_id: str,
    #     new_name: str,
    #     instructors: list = [],
    #     TAs: list = [],
    # ) -> None:
    #     _data = {
    #         "name": f"{new_name}",
    #         "termId": f"{term_id}",
    #         "availability": {
    #             "available": "No",
    #             "duration": {
    #                 "type": "Continuous",
    #             },
    #         },
    #     }

    #     update_course = (
    #         f"{self.parent.ORG_DOMAIN}/learn/api/public/v3/courses/courseId:{course_id}"
    #     )

    #     response = patch(
    #         update_course,
    #         headers={
    #             "Authorization": "Bearer " + get_access_token(),
    #             "Content-Type": "application/json",
    #         },
    #         json=_data,
    #     )

    #     # print(response.text)

    #     if response.status_code == 200:
    #         ##data = res_user_data.json()
    #         Logger.info(
    #             f"Course {course_id} has been renamed to {new_name} and put in {self.get_term_from_raw_id(term_id)} term"
    #         )
    #         for i in instructors:
    #             self.enroll_user(user_id=i, course_id=course_id, role="Instructor")
    #         for t in TAs:
    #             self.enroll_user(
    #                 user_id=t, course_id=course_id, role="TeachingAssistant"
    #             )


    #TODO: Untested
    # def update_course_datasource(self, course_id: str, data_source_id: str) -> None:
    #         _data = {
    #             "dataSourceId": data_source_id,
    #         }

    #         update_course = f"{self.parent.ORG_DOMAIN}/learn/api/public/v3/courses/courseId:{course_id}"

    #         response = patch(
    #             update_course,
    #             headers={
    #                 "Authorization": "Bearer " + get_access_token(),
    #                 "Content-Type": "application/json",
    #             },
    #             json=_data,
    #         )

    #         if response.status_code == 200:
    #             self.parent.logger.info(
    #                 f"Course {course_id}'s datasource has been changed to {data_source_id}"
    #             )



    # def update_course_availability(self, course_id: str, availability: str) -> None:
    #     if availability in ["Yes", "No", "Disabled"]:
    #         _data = {
    #             "availability": {
    #                 "available": f"{availability}",
    #             },
    #         }

    #         update_course = f"{self.parent.api_base_url}/learn/api/public/v3/courses/courseId:{course_id}"

    #         response = patch(
    #             update_course,
    #             headers={
    #                 "Authorization": "Bearer " + get_access_token(),
    #                 "Content-Type": "application/json",
    #             },
    #             json=_data,
    #         )

    #         if response.status_code == 200:

    #             self.parent.logger.info(
    #                 f"Course {course_id}'s availability has been changed to {availability}"
    #             )
    #     else:
    #         print(f"{availability} is not a valid option")

    # TODO: remove modified date, not accurate
    #TODO: do i need CourseId:
    # FIXME: Does this work????
    def _get_course(self, course_raw_id: str) -> BBCourse:
        
        # get_course_data = (
        #     f"{self.parent.api_base_url}/learn/api/public/v3/courses/{course_raw_id}"
        # )

        url = self.parent.endpoints.get_course_by_raw_id(course_raw_id=course_raw_id)

        # res_user_data = get(
        #     get_course_data,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        response = self.parent.get(url=url)

        if response.status_code == 200:
            course = response.json()
            course_obj: BBCourse = BBCourse(
            course.get("externalId"),
            course.get("name"),
            course.get("created", "01/1/1992"),
            course.get("modified", "01/1/1992"),
            course.get("termId"),
            course.get("availability", {}).get("available"),
        )
            return course_obj
        else:
            raise BlackboardAPIError(f"Failed to fetch course. {response.text}")

    

    def get_local_id(self, external_id: str):
        get_course = (
            f"{self.parent.ORG_DOMAIN}/learn/api/public/v3/courses/{external_id}"
        )

        # response = get(
        #     get_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        response = self.parent.get(url=get_course)

        #TODO: Add other codes
        if response.status_code == 200:
            course_id = response.json().get("courseId", "")
            return course_id

    

    # This works. Been tested
    def get_users_in_course_by_role(self, course_id: str, role: str = "") -> list:
        """
        Gets a list of users in a course. If role is blank, will return all users.

        Args:
            course_id (str): The unique user ID of the course to be gathered.
            role (str): _description_

        Returns:
            List: _description_
        """
        #get_list = f"{self.parent.api_base_url}/learn/api/public/v1/courses/externalId:{course_id}/users"
        url = self.parent.endpoints.course_users(course_id=course_id)
        _all_users = []
        _users = []

        # res_user_data = get(
        #     get_list,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        res_user_data = self.parent.get(url=url)

        if res_user_data.status_code == 200:
            _all_users = res_user_data.json().get("results", [])

        if role == "":
            return _all_users

        else:
            for user in _all_users:
                if user.get("courseRoleId") == role:
                    _users.append(user)

            return _users

    def __update_course_membership(
        self, course_id: str, username: str, course_role: str = "Student"
    ) -> None:
        _data = {
            "courseRoleId": f"{course_role}",
        }

        #update_course = f"{self.parent.ORG_DOMAIN}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{username}"

        url = self.parent.endpoints.course_user(course_id=course_id, username=username)

        # response = patch(
        #     update_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        #     json=_data,
        # )

        response = self.parent.patch(url=url, json=_data)


        # TODO: Make error info better
        match response.status_code:
            case 200:
                self.parent.logger.info(
                    f"{username} role has been changed to {course_role} in course {course_id}"
                )
            case 400:
                self.parent.logger.error("The request did not specify valid data")
            case 403:
                self.parent.logger.error("User has insufficient privileges")
            case 404:
                self.parent.logger.error("Course not found or course membership not found")
            case 409:
                self.parent.logger.error("Conflict?? what does that even mean")

    def delete_course(self, course_id: str) -> None:
        """
        Delete a course from the database.

        Args:
            course_id (str): The unique identifier of the course to be deleted.
        """
        _delete_course = (
            f"{self.parent.ORG_DOMAIN}/learn/api/public/v3/courses/courseId:{course_id}"
        )

        # _response = delete(
        #     _delete_course,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        _response = self.parent.delete(_delete_course)

        if _response.status_code == 202:
            self.parent.logger.info(f"{course_id} was deleted.")
        else:
            #print(f"Request failed, check logs. {Logger.get_file_path()}")
            self.parent.logger.error(f"Failed to delete course {course_id}. {_response.text}")

    #TODO: Work in progress
    def get_content(self, course_id: str) -> list:
        get_list = f"{self.parent.api_base_url}/learn/api/public/v1/courses/courseId:{course_id}/contents"

        # res_user_data = get(
        #     get_list,
        #     headers={
        #         "Authorization": "Bearer " + get_access_token(),
        #         "Content-Type": "application/json",
        #     },
        # )

        res_user_data = self.parent.get(url=get_list)

        if res_user_data.status_code == 200:
            _all_users = res_user_data.json()  # .get("results", [])
            print(json.dumps(_all_users, indent=4))

            # return _users

