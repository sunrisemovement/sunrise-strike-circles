def get_model_type(model):
	"""
	Fetch the name of a Django model.
	"""
	return model._meta.model_name