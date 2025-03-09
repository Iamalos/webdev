# AUTOGENERATED! DO NOT EDIT! File to edit: Contacts_v2.ipynb.

# %% auto 0
__all__ = ['app', 'rt', 'contacts', 'Contact', 'page_heading', 'add_button', 'filter_contacts', 'contacts_table',
           'action_buttons', 'validate_contact', 'handle_contact_save', 'contact_form', 'contact_detail',
           'create_toast', 'get', 'post', 'delete']

# %% Contacts_v2.ipynb 2
from fasthtml.common import *
from fasthtml.jupyter import JupyUvi, HTMX
from monsterui.all import *
import json

# %% Contacts_v2.ipynb 3
app,rt,contacts,Contact = fast_app("data/contacts.db",hdrs=Theme.blue.headers(),
                                    id=int, first=str, last=str, phone=str, email=str, errors=str,
                                    pk="id", live=True)

# %% Contacts_v2.ipynb 4
if not contacts(): 
    with open("contacts.json","r") as f: data = json.load(f)
    contacts.insert_all(data)

# %% Contacts_v2.ipynb 6
def filter_contacts(q=None):
    """Filter contacts that have `q` in first name, last name or email"""
    if not q: return contacts(order_by="id")
    q = q.lower()
    return [o for o in contacts(order_by="id")
            if q in (o.first or "").lower()
            or q in (o.last or "").lower()
            or q in (o.email or "").lower()]

def contacts_table(q=None):
    """Create a table with contacts applying a filter is query was provided"""
    rows = filter_contacts(q)
    return Table(
        Thead(
            Tr(*[Th(col) for col in ["First", "Last", "Phone", "Email", "Actions"]])
        ),
        Tbody(
            *[Tr(
                Td(c.first or ""),
                Td(c.last or ""),
                Td(c.phone or ""),
                Td(c.email or ""),
                Td(action_buttons(c))
            ) for c in rows]
        ),
        cls=(TableT.hover, TableT.divider, TableT.responsive),
        id="contacts-table")

def action_buttons(contact):
    """Add buttons to view and edit contact"""
    return DivHStacked(
        Button(UkIcon("eye", cls="mr-2"), "View", cls=ButtonT.ghost, hx_get=f'/contacts/{contact.id}', hx_target='#modal-container'),
        Button(UkIcon("pencil", cls="mr-2"),"Edit", cls=ButtonT.ghost, hx_get=f'/contacts/{contact.id}/edit', hx_target='#modal-container'))

# %% Contacts_v2.ipynb 7
def validate_contact(contact, # The contact object to validate
                     id=None # Optional ID for existing contacts (to check email uniqueness)
                    ):
    """ Validates contact data and returns a dictionary of errors."""
    errors = {}
    if not contact.first: errors["first"] = "First name is required"
    if not contact.email: errors["email"] = "Email is required"
    elif any(c.email == contact.email and (c.id != id) for c in contacts()): errors["email"] = "Email already exists" 
    
    # Additional validations could be added here:
    # - Email format validation
    # - Phone number format validation
    # - Name length restrictions
    # - etc.
    return errors

# %% Contacts_v2.ipynb 8
def handle_contact_save(contact, id=None):
    """Common logic for saving a contact (create or update)"""
    errors = validate_contact(contact, id)

    if errors: 
        contact.errors = json.dumps(errors)
        action = '/contacts/create' if id is None else f'/contacts/{id}/update'
        return Modal(
            contact_form(contact, action), 
            header=ModalHeader(H3("Edit Contact" if id else "Add Contact")),
            id="contact-modal", open=True)

    if id:
        # Update existing contact
        contact.id = id
        contacts.update(contact)
        message = "Contact updated successfully!"
    else:
        # Create new contact
        contacts.insert(contact)
        message = "Contact added successfully!"

    # create an out-of-band replacement for the contacts table and success toast
    updated_table = Div(contacts_table(),id="contacts-table", hx_swap_oob="true")
    success_toast = create_toast(message)
    
    return Div(updated_table, success_toast)

# %% Contacts_v2.ipynb 9
def contact_form(contact=None, action="/contacts/create"):
    """Reusable form that works both for new and edit"""

    # parse errors if they exist
    errors = json.loads(contact.errors) if contact and contact.errors else {}

    is_edit = contact and hasattr(contact, "id") and contact.id

    delete_button = Button(
        UkIcon("trash-2", cls=(TextT.error, "text-white mr-2")), "Delete", cls=ButtonT.destructive, 
        hx_get=f"/contacts/{contact.id}/confirm", hx_target="#modal-container"
    ) if is_edit else None
    
    return Form(
        Grid(
            Div(
                LabelInput("First Name", id="first", placeholder="First Name", value=contact.first if contact else ""),
                P(errors.get("first", ""), cls=(TextT.error, TextT.sm,"mt-1")) if "first" in errors else None),
            Div(
                LabelInput("Last Name", id="last", placeholder="Last Name", value=contact.last if contact else "")),
            cols=2),
        Grid(
            Div(
                LabelInput("Phone", id="phone", placeholder="Phone", value=contact.phone if contact else "")),
            Div(
                LabelInput("Email", id="email", type="email", placeholder="Email", value=contact.email if contact else ""),
                P(errors.get("email",""), cls=(TextT.error, TextT.sm,"mt-1")) if "email" in errors else None),
            cols=2),
        
        DivFullySpaced(
            delete_button,
            DivHStacked(
                ModalCloseButton("Cancel", cls=ButtonT.ghost),
                Button("Save", cls=ButtonT.primary, type="submit"),
                cls="space-x-2"
            )
        ),
        hx_post=action, hx_target="#modal-container"
    )

# %% Contacts_v2.ipynb 10
def contact_detail(contact):
    """Detail view for a contact"""
    return Modal(
        ModalBody(
            # Use a single centered container for the entire content
            DivCentered(
                H4(f"{contact.first or ''} {contact.last or ''}", cls=(TextT.bold, TextT.center, "mb-6")),
                DivLAligned(UkIcon('phone', cls='mr-2 text-primary'), P(contact.phone or '-'), cls="mb-4 justify-center"),
                DivLAligned(UkIcon('mail', cls='mr-2 text-primary'), P(contact.email or '-'), cls="justify-center"),
                cls="items-center py-4"
            )
        ),
        header = ModalHeader(H3("Contact Details")),
        footer = DivFullySpaced(
            ModalCloseButton("Close", cls=ButtonT.primary),
            Button(UkIcon("pencil", cls="mr-2"), "Edit", cls=ButtonT.primary, hx_get=f"/contacts/{contact.id}/edit", hx_target="#modal-container")
        ),    
        id = "contact-modal",
        open=True)

# %% Contacts_v2.ipynb 11
def create_toast(msg, #  The message to display in the toast
                 icon="check-circle", # Name of the icon to display (from Lucide icons)
                 alert_type=AlertT.success, # The type of alert (success, warning, error, info)
                 position=(ToastHT.center, ToastVT.middle)): # Tuple of horizontal and vertical position classes
    """Creates a standardized toast notification configured for out-of-band swapping"""
    icon_color = {
        AlertT.success: TextT.success,
        AlertT.warning: TextT.warning,
        AlertT.error: TextT.error,
        AlertT.info: TextT.info
    }.get(alert_type, TextT.primary)

    return Toast(
        DivLAligned(UkIcon(icon,cls=f"mr-2 {icon_color}"), Span(msg)),
        id="toast", alert_cls=alert_type, cls=position, hx_swap_oob="true", hx_get="/dismiss-toast", hx_trigger="load delay:3s", hx_target="#toast")

# %% Contacts_v2.ipynb 13
page_heading = Div(cls="space-y-2")(H1("Contacts"), P("Manage your contacts!", cls=TextPresets.muted_sm))

add_button = DivLAligned(
    Button(UkIcon("plus-circle", cls="mr-2"), "Add Contact", cls=ButtonT.primary, hx_get="/contacts/new", hx_target="#modal-container"),
    cls="mb-4 mt-4")

# %% Contacts_v2.ipynb 15
@rt("/")
def get(): return Redirect("/contacts")

# We can also use htmx_post instrad of htmx_get and sklip hx_include
@rt("/contacts")
def get(q:str=None):
    search = Form(
        DivHStacked(
            Input(name="q", value=q, placeholder="Search contacts...", cls="w-full md:w-2/3 lg:w-1/2", hx_get="/contacts/search",
                  hx_trigger="keyup changed delay:500ms", hx_target="#contacts-table", hx_include='[name="q"]'),
            Button("Search", type="submit")),
       cls="mt-8")
    return Container(page_heading, search, contacts_table(q), add_button, Div(id="modal-container"), Div(id="toast"))

# %% Contacts_v2.ipynb 17
@rt("/contacts/search")
def get(q: str = ''): return contacts_table(q)

# %% Contacts_v2.ipynb 19
@rt("/contacts/{id:int}/edit")
def get(id:int):
    contact=contacts[id]
    
    return Modal(
        contact_form(contact, action=f"/contacts/{id}/update"),
        header=ModalHeader(H3("Edit Contact")),
        id="contact-modal",
        open=True)

# %% Contacts_v2.ipynb 20
@rt("/contacts/{id:int}/update")
def post(id: int, contact: Contact):
    return handle_contact_save(contact, id)

# %% Contacts_v2.ipynb 22
@rt("/contacts/new")
def get():
    """Create a modal for adding a contact"""
    return Modal(
        contact_form(),
        header=ModalHeader(H3("Add Contact")),
        id="contact-modal",
        open=True
    )

@rt("/dismiss-toast")
def get(): return Div(id="toast")  

# %% Contacts_v2.ipynb 23
#Try routing to /new as in the book
@rt("/contacts/create")
def post(contact: Contact):
    return handle_contact_save(contact)

# %% Contacts_v2.ipynb 25
@rt("/contacts/{id:int}")
def get(id:int): return contact_detail(contacts[id])

# %% Contacts_v2.ipynb 27
@rt("/contacts/{id:int}/confirm")
def get(id:int):
    """Confirmation modal for deleting a contact"""
    contact = contacts[id]
    return Modal(
        ModalBody(
            DivCentered(
                UkIcon("alert-triangle",cls="text-error mb-4 h-12 w-12"),
                H4("Are you sure you want to delete this contact?", cls="text-center mb-2"),
                P(f"{contact.first} {contact.last}", cls=(TextT.center,TextT.medium)),
                P("This action cannot be undone.", cls=(TextT.center, TextT.error)),
                cls="py-6"
            )
        ),
        header=ModalHeader(H3("Confirm Deletion")),
        footer=DivRAligned(
            ModalCloseButton("Cancel", cls=ButtonT.ghost), 
            # hx_confirm="Are you sure you want to delete this contact?" can be added to have a pop up to confirm the action
            Button("Delete", cls=ButtonT.destructive, hx_delete=f"/contacts/{id}", hx_target="#modal-container")),
    id="contact-modal",
    open=True)

@rt("/contacts/{id:int}")
def delete(id:int):
    """Delete a contact"""
    contact = contacts[id]
    name=f"{contact.first} {contact.last}".strip()
    contacts.delete(id)
    
    updated_table = Div(contacts_table(), id="contacts-table", hx_swap_oob="true")
    success_toast = create_toast(f"Contact {name} has been deleted", icon="trash-2", alert_type=AlertT.warning)
    
    return Div(updated_table, success_toast)

# %% Contacts_v2.ipynb 34
serve()
