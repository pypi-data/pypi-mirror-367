from .utils import *
from colorama import Fore, Style

class CreateServiceCommand:
    def __init__(self, subparsers):
        parser = subparsers.add_parser("create-service", help='Create a new service')
        parser.add_argument("app_path", type=str, help='The relative path of the app within the project (for example, "apps/app1")')
        parser.add_argument("entity_name", type=str, help='The name of the entity')
        parser.set_defaults(func=self.execute)         

    def execute(self, args):
        self.create_service(args.app_path, args.entity_name)

    def create_service(self, app_path, entity_name="Entity", **kwargs):
        """Crea un nuevo servicio"""
        services_dir = os.path.join(app_path, 'services')
        services_path = os.path.join(services_dir, entity_name.lower() + '_service.py')

        # Crear directorios si no existen
        try:
            os.makedirs(services_dir, exist_ok=True)

            # Crear archivos __init__.py
            create__init__files(services_dir)
        except OSError as e:
            print(Fore.RED + f"Failed to create directory '{services_dir}': {e}" + Style.RESET_ALL)
            return
        
        #si ya existe el archivo mostrar error
        if os.path.exists(services_path):
            print(Fore.RED + f"The file '{services_path}' already exists. A separate file cannot be created" + Style.RESET_ALL)
            return

        # Escribir imports en el archivo 
        # si no existe el archivo template_imports
        if not os.path.exists(services_path):
            #renderizar imports
            rendered_content_imports = renderTemplate(templateName = 'services', fileName='imports.py', render_params={'entity_name':entity_name})

            # Escribir imports en el archivo
            with open(services_path, 'w') as f:
                f.write(rendered_content_imports + '\n')
            print(f"Imports of Service for '{entity_name}' created at {services_path}")


        #renderizar class con crud
        rendered_content_class = renderTemplate(templateName = 'services', fileName='class_crud.py', render_params={'entity_name':entity_name})
      

        # Escribir class en el archivo
        with open(services_path, 'a') as f:
            f.write('\n' + rendered_content_class + '\n')
        print(f"Class of Service for '{entity_name}' created at {services_path}")        