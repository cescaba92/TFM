from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from produccion_app import views

app_name = 'produccion_app'

urlpatterns = [
    path('venta/',views.OrdenesVentaListView.as_view(),name='ordenes_venta'),
    path('venta/nuevo',views.OrdenesVentaCreateView.as_view(),name='nueva_orden_venta'),
    path('venta/modificar/<int:pk>',views.OrdenesVentaUpdateView.as_view(),name='modificar_orden_venta'),
    path('venta/eliminar-producto/<int:pk>',views.delete_DetalleOrdenVenta,name='eliminar_producto_venta'),
    path('venta/cancelar/<int:pk>',views.delete_OrdenVenta,name='cancelar_orden_venta'),
    path('venta/terminar-produccion/<int:pk>',views.terminar_ProduccionVenta,name='fin_produccion_orden_venta'),
    path('produccion/nuevo/<int:pk>',views.nueva_ordenProduccion,name='nueva_orden_produccion'),
    path('produccion/',views.OrdenesProduccionListView.as_view(),name='ordenes_produccion'),
    path('produccion/modificar/<int:pk>',views.OrdendeProduccionUpdateView.as_view(),name='modificar_produccion'),
    path('produccion/modificar_orden/<int:pk>',views.consultar_ordenProducción,name='modificar_ver_produccion'),
    path('produccion/cancelar/<int:pk>',views.cancelar_ordenProduccion,name='cancelar_produccion'),
    path('produccion/enviar_orden/<int:pk>',views.enviar_orden,name='enviar_orden_suministro'),
    path('produccion/orden/enprogreso/<int:pk>',views.actualizar_produccion,name='enviar_orden_progreso'),
    path('produccion/orden/completar/<int:pk>',views.completar_produccion,name='completar_orden'),
    path('produccion/suministros/modificar/<int:pk>',views.OrdenSuministroUpdateView.as_view(),name='modificar_suministro'),
    path('produccion/suministros/completar/<int:pk>',views.completar_OrdenSuministro,name='completar_orden_suministro'),
    path('produccion/suministros/eliminar-emision/<int:pk>',views.delete_SuministroEmision,name='eliminar_suministroEmision'),
    path('produccion/suministros/eliminar-tramo/<int:pk>',views.delete_SuministroViaje,name='eliminar_suministroTramo'),
    path('produccion/suministros/cancelar/<int:pk>',views.cancelar_Suministro,name='cancelar_suministro'),
    path('produccion/actividades/modificar/<int:pk>',views.ActividadesProduccionInLineUpdateView.as_view(),name='modificar_actividad_orden'),
    path('produccion/actividades/eliminar/<int:pk>',views.delete_OrdenActividad,name='eliminar_actividad_orden'),
    path('produccion/actividades/eliminar-emision/<int:pk>',views.delete_ActividadEmision,name='eliminar_actividadEmision'),
    path('produccion/actividades/enprogreso/<int:pk>', views.iniciar_ActividadProduccion,name='enviar_actividad_progreso'),
    path('produccion/actividades/terminar/<int:pk>', views.terminar_ActividadProduccion,name='completar_actividad'),
    path('entrega/nuevo/<int:pk>',views.OrdenEntregaCreate,name="crear_orden_entrega"),
    path('entrega/modificar/<int:pk>',views.OrdenEntregaUpdateView.as_view(),name='editar_orden_entrega'),
    path('entrega/actividades/modificar/<int:pk>',views.Actividad_EnvioInLineUpdateView.as_view(),name='modificar_actividad_entrega'),
    path('entrega/actividades/eliminar-emision/<int:pk>',views.delete_ActividadEntregaEmision,name='eliminar_actividadEnvioEmision'),
    path('entrega/actividades/enprogreso/<int:pk>', views.iniciar_ActividadEntrega,name='enviar_actividadEnvio_progreso'),
    path('entrega/actividades/terminar/<int:pk>', views.terminar_ActividadEntrega,name='completar_actividad_envio'),
    path('entrega/actividades/eliminar/<int:pk>',views.delete_OrdenEntregaActividad,name='eliminar_actividad_envio'),
    path('entrega/enviar_orden/<int:pk>',views.enviar_OrdenEntregaActividad,name='enviar_orden_entrega'),
    path('entrega/recepcion_orden/<int:pk>',views.recepcion_OrdenEntregaActividad,name='recepcion_orden_entrega'),
    path('entrega/tramos/eliminar-tramo/<int:pk>',views.delete_EntregaViaje,name='eliminar_EntregaTramo'),
    path('entrega/',views.OrdenEntregaListView.as_view(),name='ordenes_entrega'),

    #path('plan/nuevo/<int:pk>',views.CadenaSuministroCreateView.as_view(),name='add_cadena'),
    #path('plan/update/<int:pk>',views.CadenaSuministroUpdateView.as_view(),name='update_cadena1'), 
    #path('plan/cargar_suministros/',views.cargar_suministros,name='cargar_suministros'),
    #path('plan/cargar_midpoints/',views.cargar_midpoints,name='cargar_midpoints'),
    #path('plan/suministros/emisiones/<int:pk>',views.Suministro_PlanCadenaUpdateView.as_view(),name='add_emisionplan'),
    #path('plan/suministros/delete/<int:pk>',views.delete_CadenaSuministro,name='delete_cadenasuministro'),
    #path('plan/suministros/delete-emision/<int:pk>',views.delete_SuministroEmision,name='delete_suministroEmision'),
    #path('plan/suministros/delete-tramo/<int:pk>',views.delete_SuministroViaje,name='delete_suministroTramo'),
    #path('plan/tramos/delete/<int:pk>',views.delete_TramoPlan,name='delete_tramoplan'),
    #path('plan/actividades/emisiones/<int:pk>',views.Actividades_PlanCadenaUpdateView.as_view(),name='add_emisionact'),
    #path('plan/actividades/delete-emision/<int:pk>',views.delete_ActividadesEmision,name='delete_actividadEmision'),
    #path('plan/actividades/delete/<int:pk>',views.delete_CadenaActividad,name='delete_actividadcadena'),
    
]
