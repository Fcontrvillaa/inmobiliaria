# Inmobiliaria Conecta



1. Modelo de Usuario Personalizado (portal/models.py)
Se utilizó un modelo PerfilUser que hereda de AbstractUser. Esto permite añadir campos específicos del negocio, como tipo_usuario y rut, directamente al modelo de usuario, facilitando las consultas y la lógica de negocio sin necesidad de un modelo de perfil separado con una relación OneToOne.

2. Vistas Basadas en Clases (CBV) (portal/views.py)
El proyecto aprovecha las Vistas Basadas en Clases de Django para un código más estructurado y reutilizable:

HomeInmuebleListView: Para listar objetos.

PerfilView (TemplateView): Para construir una página compleja que consolida múltiples consultas.

SolicitudArriendoCreateView (CreateView): Para manejar la lógica de formularios de creación.

PerfilInmuebleUpdateView y PerfilInmuebleDeleteView: Para las operaciones del CRUD de inmuebles.

3. Seguridad y Control de Acceso
LoginRequiredMixin: Se utiliza en las vistas de perfil y creación de solicitudes para asegurar que solo los usuarios autenticados puedan acceder.

Validación de Propietario: Las vistas que modifican datos (ej. solicitud_aceptar, PerfilInmuebleUpdateView) incluyen filtros en las consultas para garantizar que un usuario solo pueda modificar los recursos que le pertenecen.

Python

# Ejemplo en `solicitud_aceptar`
s = get_object_or_404(SolicitudArriendo, pk=pk, inmueble__propietario=request.user)
4. Optimización de Consultas a la Base de Datos
En la vista PerfilView, se utiliza select_related para optimizar las consultas y evitar el problema N+1. Al obtener las solicitudes, se traen los datos del inmueble y la comuna en una sola consulta SQL, mejorando el rendimiento.

Python

# portal/views.py -> PerfilView
ctx["enviadas"] = u.solicitudes_enviadas.select_related("inmueble", "inmueble__comuna").order_by("-creado")
5. Lógica de Negocio en Vistas y Plantillas
La regla de que "un propietario no puede arrendar su propia propiedad" se implementa en dos capas:

Frontend (web/home.html): Se deshabilita el botón de "Solicitar" en la plantilla si el usuario autenticado es el propietario, mejorando la experiencia de usuario.

Backend (portal/views.py): Se añade una validación en el método dispatch de SolicitudArriendoCreateView como medida de seguridad final, en caso de que el usuario intente acceder a la URL manualmente.