
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# importa las excepciones personalizadas
from .domain.exceptions import (
    PromotionValueError,
    PromotionValidationError,
    PromotionAlreadyExistsError,
    PromotionNotFoundError,
    PromotionOperationNotAllowedError,
    PromotionPermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app1.promotion_forms import (
    PromotionCreateForm, 
    PromotionEditGetForm, 
    PromotionEditPostForm, 
    PromotionViewForm
)

# Importar servicios específicos del dominio
from app1.services.promotion_service import PromotionService

# Importar repositorios específicos de la infraestructura
from app1.infrastructure.promotion_repository import PromotionRepository


def promotion_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de promotion.
    """

    promotionList = [] #inicialize list

    promotionService = PromotionService(repository=PromotionRepository()) # Instanciar el servicio

    # Obtener la lista del repositorio
    try:
        promotionList = promotionService.list()

    except (PromotionValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app1/promotion_web_list.html', {
        'promotionList': promotionList
    })


def promotion_create(request):
    """
    Vista genérica para crear una nueva instancia de promotion utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = PromotionCreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            promotionService = PromotionService(repository=PromotionRepository()) # Instanciar el servicio

            # Obtener el ID de la entidad relacionada si existe
            external_id = request.POST.get('external_id', None)

            # Obtener la lista de ids de externals seleccionadas
            externals_ids = form_data.get('externals', [])

            try:
                # LLamar al servicio de creación
                promotionService.create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created promotion")
                return redirect('app1:promotion_list')

            except PromotionAlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (PromotionValueError, PromotionValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = PromotionCreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/promotion_web_create.html', {'form': form}) 


def promotion_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de promotion utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app1:promotion_list')

    promotionService = PromotionService(repository=PromotionRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        promotion = promotionService.retrieve(entity_id=id)

    except PromotionNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app1:promotion_list')
    except PromotionValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app1:promotion_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app1:promotion_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app1:promotion_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = PromotionEditPostForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            try:
                # obtenemos del request los campos especiales del formulario
                # ejemplo: password = request.POST.get('password', None)
                # ejemplo: photo = request.FILES.get('photo', None)
                # y los enviamos como parametros al servicio de actualizacion

                # Obtener el ID de la entidad relacionada si existe
                external_id = request.POST.get('external_id', None)

                # Obtener la lista de ids de externals seleccionadas
                externals_ids = form_data.get('externals', [])                

                # LLamar al servicio de actualización
                promotionService.update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated promotion")

                # Redireccionar a la lista de promotions
                return redirect('app1:promotion_list')

            except PromotionNotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (PromotionValueError, PromotionValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = PromotionEditGetForm(initial={
            'id': promotion['id'],            
            'attributeName': promotion['attributeName'],
            'attributeEmail': promotion['attributeEmail']
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app1/promotion_web_edit.html', {'form': form})


def promotion_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de promotion.
    """
    if id is None:
        return redirect('app1:promotion_list')

    promotionService = PromotionService(repository=PromotionRepository()) # Instanciar el servicio

    try:
        # Obtener los datos de la entidad desde el servicio
        promotion = promotionService.retrieve(entity_id=id)

    except PromotionNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app1:promotion_list')
    except PromotionValueError as e:
        messages.error(request,  str(e))
        return redirect('app1:promotion_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app1:promotion_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app1:promotion_list')

    # Renderizar la plantilla con el formulario de vista
    form = PromotionViewForm(initial={
        'attributeName': promotion['attributeName'],
        'attributeEmail': promotion['attributeEmail']
    })

    return render(request, 'app1/promotion_web_detail.html', {'form': form})


def promotion_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de promotion utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app1:promotion_list')

    promotionService = PromotionService(repository=PromotionRepository()) # Instanciar el servicio

    try:
        # LLamar al servicio de eliminación
        promotionService.delete(entity_id=id)
        messages.success(request, f"Successfully deleted promotion")

    except PromotionNotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (PromotionValueError, PromotionValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app1:promotion_list')

