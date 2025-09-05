from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages 
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .form import RegisterForm, LoginForm
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Prefetch



from .models import (
    Region,
    Comuna,
    Inmueble,
    SolicitudArriendo,
    PerfilUser
)

from .form import (
    RegionForm,
    ComunaForm,
    InmuebleForm,
    SolicitudArriendoForm,
    PerfilUserForm
)

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)

# Create your views here.

def home(request):
    return render(request, "web/home.html")



# CRUD PARA Region

class RegionListView(ListView):
    model = Region
    template_name = "inmuebles/region_list.html"
    context_object_name = "regiones"

class RegionCreateView(CreateView):
    model = Region
    form_class = RegionForm
    template_name = "inmuebles/region_form.html"
    success_url = reverse_lazy("region_list")


class RegionUpdateView(UpdateView):
    model = Region
    form_class = RegionForm
    template_name = "inmuebles/region_form.html"
    success_url = reverse_lazy("region_list")

class RegionDelete(DeleteView):
    model = Region  
    template_name = "inmuebles/region_confirm.html"
    success_url = reverse_lazy("region_list")



#CRUD PARA COMUNA 


class ComunaListView(ListView):
    model = Comuna
    template_name = "inmuebles/comuna_list.html"
    context_object_name = "comunas"


class ComunaCreateView(CreateView):
    model = Comuna
    form_class = ComunaForm
    template_name = "inmuebles/comuna_form.html"
    success_url = reverse_lazy("comuna_list")


class ComunaUpdateView(UpdateView):
    model = Comuna
    form_class = ComunaForm
    template_name = "inmuebles/comuna_form.html"
    success_url = reverse_lazy("comuna_list")


class ComunaDeleteView(DeleteView):
    model = Comuna
    template_name = "inmuebles/comuna_confirm.html"
    success_url = reverse_lazy("comuna_list")



#CRUD PARA Inmueble


class InmuebleDetailView(DetailView):
    model = Inmueble
    template_name = "inmuebles/inmueble_detail.html"
    context_object_name = "inmueble"


class InmueblesListView(ListView):
    model = Inmueble
    template_name = "web/home.html"
    context_object_name = "inmuebles"


class InmuebleCreateView(CreateView):
    model = Inmueble
    form_class = InmuebleForm
    template_name = "inmuebles/inmueble_form.html"
    success_url = reverse_lazy("inmueble_list")
    success_url = reverse_lazy("home")


class InmuebleUpdateView(UpdateView):
    model = Inmueble
    form_class = InmuebleForm
    template_name = "inmuebles/inmueble_form.html"
    success_url = reverse_lazy("inmueble_list")
    success_url = reverse_lazy("home")


class InmuebleDeleteView(DeleteView):
    model = Inmueble
    template_name = "inmuebles/inmueble_confirm.html"
    success_url = reverse_lazy("inmueble_list")
    success_url = reverse_lazy("home")


#CRUD PARA Solicitud Arriendo

class SolicitudArriendoListView(ListView):
    model = SolicitudArriendo
    template_name = "inmuebles/solicitudes_list.html"
    context_object_name = "solicitudes"


@method_decorator(login_required, name="dispatch")
class SolicitudArriendoCreateView(CreateView):
    model = SolicitudArriendo
    form_class = SolicitudArriendoForm
    template_name = "inmuebles/solicitud_form.html"
    success_url = reverse_lazy("perfil")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inmueble_pk = self.kwargs.get('inmueble_pk')
        inmueble = get_object_or_404(Inmueble, pk=inmueble_pk)
        context['inmueble'] = inmueble
        return context

    def form_valid(self, form):
        if self.request.user.tipo_usuario != 'ARRENDATARIO':
            messages.error(self.request, "Solo los arrendatarios pueden enviar solicitudes.")
            return redirect('home')

        inmueble_pk = self.kwargs.get('inmueble_pk')
        form.instance.inmueble = get_object_or_404(Inmueble, pk=inmueble_pk)
        form.instance.arrendatario = self.request.user
        messages.success(self.request, "Tu solicitud ha sido enviada correctamente.")
        return super().form_valid(form)


class SolicitudArriendoUpdateView(UpdateView):
    model = SolicitudArriendo
    form_class = SolicitudArriendoForm
    template_name = "inmuebles/inmueble_form.html"
    success_url = reverse_lazy("solicitud_list")


class SolicitudArriendoDeleteView(DeleteView):
    model = SolicitudArriendo
    template_name = "inmuebles/solicitud_confirm.html"
    success_url = reverse_lazy("solicitud_list")



#CRUD PARA PerfilUser

class PerfilUserUpdateView(UpdateView):
    model = PerfilUser
    form_class = PerfilUserForm
    template_name = "usuarios/perfil_form.html"
    success_url = reverse_lazy("perfil")


@method_decorator(login_required, name="dispatch")
class PerfilView(TemplateView):
    template_name = "usuarios/perfil.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user

        # Solicitadas por mí (si soy arrendatario)
        enviadas = (
            u.solicitudes_enviadas
            .select_related("inmueble", "inmueble__comuna")
            .order_by("-creado")
        )

        # Recibidas en mis inmuebles (si soy arrendador)
        recibidas = (
            SolicitudArriendo.objects
            .filter(inmueble__propietario=u)
            .select_related("inmueble", "inmueble__comuna", "arrendatario")
            .order_by("-creado")
        )

        # Inmuebles del arrendador
        inmuebles_propios = None
        if u.tipo_usuario == 'ARRENDADOR':
            inmuebles_propios = Inmueble.objects.filter(propietario=u)

        ctx.update({
            "enviadas": enviadas,
            "recibidas": recibidas,
            "inmuebles": inmuebles_propios,
        })
        return ctx



#login/logout/register
###########################################################

#AUTH
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Has iniciado sesión.")
        return redirect("perfil")
    return render(request, "registration/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("home")


#PERFIL

@method_decorator(login_required, name="dispatch")
class PerfilInmueblesListView(ListView):
    model = Inmueble
    template_name = "usuarios/perfil.html"
    context_object_name = "inmuebles"
    paginate_by = 10

    def get_queryset(self):
        return Inmueble.objects.filter(propietario=self.request.user)

    