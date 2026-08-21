from config.database import db
from models.course import Course, Module, Lesson, Material

@staticmethod
def create_course(title,description,instructor_id):
    course = Course(title= title, des= description,int_id = instructor_id)
    db.session.add(course)
    db.session.commit()
    return course

@staticmethod
def get_all_courses():
    return Course.query.all()

@staticmethod
def create_module(course_id, title, order=1):
    module = Module(course_id=course_id, title=title, order=order)
    db.session.add(module)
    db.session.commit()
    return module

@staticmethod
def create_lesson(module_id, title, content=None, video_url=None):
    lesson = Lesson(module_id=module_id, title=title, content=content, video_url=video_url)
    db.session.add(lesson)
    db.session.commit()
    return lesson

@staticmethod
def get_lesson_by_id(lesson_id):
    return Lesson.query.get(lesson_id)

@staticmethod
def add_material(course_id, file_name, file_path, file_type, file_size_bytes):
    material = Material(
    course_id=course_id,
    file_name=file_name,
    file_path=file_path,
    file_type=file_type,
    file_size_bytes=file_size_bytes)
    db.session.add(material)
    db.session.commit()
    return material

@staticmethod
def get_material_by_id(material_id):
    return Material.querry.get(material_id)

