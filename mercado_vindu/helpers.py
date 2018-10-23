from datetime import datetime


def user_directory_path(instance, filename):
    fecha = datetime.now().date()
    return 'procesos_batch/marca_{}/{}/{}_{}/{}'.format(
        instance.marca.nombre, instance.tipo, fecha.year, fecha.month, filename)
