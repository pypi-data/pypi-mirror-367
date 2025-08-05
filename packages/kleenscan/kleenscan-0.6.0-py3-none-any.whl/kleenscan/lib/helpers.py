from functools import wraps
import inspect



def get_param_structure(method_name: str) -> dict:
    # av_list argument/parameter.
    av_list_param = {
        'required': False,
        'type': list
    }

    # Output argument/parameter structure.
    output_params_structure = {
        'out_file': {
            'required': False,
            'type': str
        },
        'output_format': {
            'required': False,
            'type': str
        }
    }

    # Argument structure
    params_map = {
        # Kleenscan.__init__
        '__init__': {
            'x_auth_token': {
                'required': True,
                'type': str
            },
            'verbose': {
                'required': False,
                'type': bool
            },
            'max_minutes': {
                'required': True,
                'type': int
            }
        },

        # Kleenscan.scan
        'scan': {
            'file': {
                'required': True,
                'type': str
            },
            'av_list': av_list_param
        },

        # Kleenscan.scan_runtime
        'scan_runtime': {
            'file': {
                'required': True,
                'type': str
            },
            'av_list': av_list_param
        },

        # Kleenscan.scan_urlfile
        'scan_urlfile': {
            'url': {
                'required': True,
                'type': str
            },
            'av_list': av_list_param
        },

        # Kleenscan.scan_url
        'scan_url': {
            'url': {
                'required': True,
                'type': str
            },
            'av_list': av_list_param
        },

        # Kleenscan.av_list
        'av_list': { **output_params_structure }
    }

    # Add output_params_structure to methods that require it.
    params_map['scan'].update(output_params_structure)
    params_map['scan_urlfile'].update(output_params_structure)
    params_map['scan_url'].update(output_params_structure)

    return params_map[method_name]



def check_types(func: callable) -> callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        sig = inspect.signature(func)
        param_structure = get_param_structure(func.__name__)
        
        # Merge args and kwargs into a dictionary of all arguments.
        bound_args = sig.bind_partial(*args, **kwargs).arguments

        # Check each argument against the expected type and constraints.
        for param_name, value in bound_args.items():
            if param_name in param_structure:
                param_type = param_structure[param_name]['type']
                required = param_structure[param_name]['required']

                # Type check.
                if value != None and not isinstance(value, param_type):
                    raise TypeError(f'Argument "{param_name}" to Kleenscan.{func.__name__} must be {param_type.__name__}, got: {type(value).__name__} with value: {value}.')
        
                # Empty string check.
                elif param_type == str and value == '':
                    raise ValueError(f'Argument "{param_name}" to Kleenscan.{func.__name__} cannot be an empty string.')
                
                # int range check.
                elif param_type == int and value <= 0:
                    raise ValueError(f'Argument "{param_name}" to Kleenscan.{func.__name__} must be a positive number, got: {value}.')
      
                # Check if all values are string in a list.
                elif param_type == list:
                    if value:
                        for element in value:
                            if not isinstance(element, str):
                                raise TypeError(f'Argument "{param_name}" to Kleenscan.{func.__name__} must be a list of strings, got: {value}.')
      

        return func(*args, **kwargs)

    return wrapper