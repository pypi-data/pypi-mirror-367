



ADD_CHILD_COURSE = "{base_url}/learn/api/public/v1/courses/courseId:{course_id}/children/courseId:{child_id}"

GET_COURSE = "{base_url}/learn/api/public/v3/courses/courseId:{course_id}"
CREATE_COURSE = "{base_url}/learn/api/public/v3/courses"

__COPY_COURSE = "{base_url}/learn/api/public/v2/courses/courseId:{course_id}/copy"

COURSE_USER = "{base_url}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{user_id}"
COURSE_GB_COLUMNS = "{base_url}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns"


#TODO: Add the rest 
def url_copy_course(base_url: str, course_id: str) -> str:
    return __COPY_COURSE.format(
        base_url=base_url,
        course_id=course_id
    )