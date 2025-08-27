import asyncio

from flask import Blueprint, render_template, Response, request, url_for, redirect

from utils import level_required


class BlueprintManager(Blueprint):
    def __init__(self, api_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_admin_blueprint_routes()
        self.api_manager = api_manager

    def _create_admin_blueprint_routes(self) -> None:
        """
        Creates rotes for admin blueprint
        :return: None
        """

        @self.route('/admin/base', endpoint='admin')
        @level_required(3)
        def base():
            """
            Base page for admins
            :return: page
            """
            return render_template('admin_index.html', title='Панель администратора')

        @self.route('/add_dish', methods=['POST', 'GET'], endpoint='add_dish')
        @level_required(3)
        def add_dish() -> str | Response:
            """
            Rotes a page where admin can to add new dish to the menu
            :return: page
            """
            if request.method == 'POST':
                name = request.form.get('dish_name')
                description = request.form.get('description')
                file = request.files.get('photo')
                price = request.form.get('price')
                category = request.form.get('category')
                with open('current_image_number.txt', 'r') as txt:
                    menu_image_counter = int(txt.readline())
                with open('current_image_number.txt', 'w') as txt:
                    txt.write(str(menu_image_counter + 1))
                img_src = f'{url_for("static", filename=(src := f"img/dishes/img_{menu_image_counter}.png"))}'[1:]
                with open(img_src, 'wb') as img:
                    img.write(file.read())
                if asyncio.run(self.api_manager.post('menu', data={
                    'dish_name': name,
                    'description': description,
                    'img_src': src,  # post new menu item to database using rest api
                    'category': category,
                    'price': price
                })):
                    return redirect('/admin/base')
            return render_template('add_dish.html', title='Добавление блюда')

        @self.route("/orders", endpoint='orders')
        @level_required(2)
        def orders():
            orders_ = asyncio.run(self.api_manager.get_api_list('orders'))
            data = orders_.get('orders')
            for el in data:
                el['correct_items_list'] = tuple(zip(el['count_list'].split(), el['position_list'].split()))
            return render_template('cooking_orders.html', title='Заказы', orders=data)

        @self.route('/manage_users', endpoint='manage_users')
        @level_required(3)
        def manage_users():
            users = asyncio.run(self.api_manager.get_api_list('users'))['users']
            users = map(lambda user: [user[key] for key in
                                      ('id', 'name', 'surname', 'sex', 'email', 'phone_number', 'user_level')], users)
            return render_template('manage_users.html', title='Управление пользователями', users=users)
