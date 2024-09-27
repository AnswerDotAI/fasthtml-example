from fasthtml.common import *
from fasthtml.components import (Sl_icon, Sl_button, Sl_menu, Sl_menu_item, Sl_menu_item, Sl_menu_item,
                                 Sl_breadcrumb, Sl_breadcrumb_item, Sl_breadcrumb_item, Sl_card)

def sl_link(*args, **kwargs): return(jsd('@shoelace-style', 'shoelace', 'cdn', *args, prov='npm', **kwargs))
app,rt = fast_app(pico=False, hdrs=(
    Meta(charset='UTF-8'),
    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
    sl_link('themes/light.css', typ='css'),
    sl_link('shoelace-autoloader.js', type='module'),
    Script(src='https://cdn.tailwindcss.com')
))

def icon(nm, text, **kw): return Sl_icon(slot='prefix', name=nm, **kw), text
def menu(nm, text, path): return Sl_menu_item(*icon(nm, text), cls='rounded-md', hx_get=path)
def breadcrumbs(*crumbs): return Sl_breadcrumb(*map(Sl_breadcrumb_item, crumbs))

@rt('/')
def get():
    return Title('My Shoelace App'), Div(
      Header(
        Div(*icon('lightning-charge-fill', 'My Shoelace App', cls='mr-2'),
            cls='text-xl font-bold flex items-center'),
      Div(
        Sl_button(
          *icon('person-circle', 'Profile'),
          variant='primary', size='small', cls='mr-2'),
        Sl_button(
          *icon('box-arrow-right', 'Logout'),
          variant='primary', size='small')
      ), cls='bg-blue-600 text-white p-4 flex justify-between items-center'),
    Div(
      Nav(
        Sl_menu(
          menu('house-door', 'Dashboard', '/users'),
          menu('graph-up', 'Analytics', '/rev'),
          menu('gear', 'Settings', '/proj'),
        ), hx_target='#metrics', cls='w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto'),
      Main(
        breadcrumbs('Home', 'Dashboard'),
        H1('Welcome to Your Dashboard', cls='text-2xl font-bold mt-4 mb-2'),
        P("Here's an overview of your latest activity and key metrics.", cls='mb-8'),
        Div(users(), id='metrics', cls='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'),
        Div(id='details'),
        cls='flex-1 p-8 overflow-y-auto'),
      cls='flex flex-1 overflow-hidden'),
    cls='h-full flex flex-col bg-gray-50')

@rt('/detl')
def get(title:str): return Div(f'Details for {title}')

def metric_card(title, value, trend):
    return Sl_card(
        Div(title, cls='text-sm text-gray-600 mb-1', hx_get=f'/detl?title={title}', hx_target='#details'),
        Div(value, cls='text-3xl font-bold mb-1'),
        Div(trend, cls='text-xs text-green-600'),
        cls='flex flex-col justify-between')

def users(): return metric_card('Total Users', '1,234', '+5.2% from last week')

@rt('/users')
def get(): return users()

@rt('/rev')
def get(): return metric_card('Revenue', '$12,345', '+2.4% from last month')

@rt('/proj')
def get(): return metric_card('Active Projects', '42', '3 new this week')

serve()
