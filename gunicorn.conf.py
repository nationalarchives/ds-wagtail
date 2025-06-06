import multiprocessing

# Dynammically set workers based on CPU count
#
# http://docs.gunicorn.org/en/19.3/design.html#how-many-workers
#
# Platform's environment appear to be very memory constrained.
# Reduce the number of workers to a quarter of the recommended number.
workers = int(multiprocessing.cpu_count() / 4) + 1
