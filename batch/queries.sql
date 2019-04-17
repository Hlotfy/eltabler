use tabtracker;


select * from orders;

insert into orders(dt,username) values(now(),"lorthsmi");

-- insert into orders(dt,username) values(now(),"lorthsmi");

insert into payments (username, dt, method, amount) values ("hlotfy", now(), "venmo", 1.50);
insert into payments (username, dt, method, amount) values ("mkashyap", now(), "cash", 0.50);

-- update user, orders, menuItem set user.balanceOwed = (select sum(menuItem.price) from orders inner join menuItem on orders.miid = menuItem.miid where orders.username=user.username) where user.username = orders.username;

-- select * from user where balanceOwed > 0;

update user, payments set balanceOwed = balanceOwed - (select sum(payments.amount) from payments where payments.username = user.username) where user.username = payments.username;

select * from recipe;

select menuItem.name, menuItem.price, sum(ingredient.price) as 'ingredients price' from recipe inner join menuItem on recipe.miid = menuItem.miid inner join ingredient on recipe.iid = ingredient.iid group by menuItem.miid order by menuItem.name;  

select recipe.miid, sum(ingredient.price) from recipe inner join ingredient on recipe.iid = ingredient.iid group by recipe.miid;

select user.name, sum(menuItem.price) as 'Tab Balance Owed' from orders inner join user on orders.username=user.username inner join orderItem on orders.oid=orderItem.oid inner join menuItem on orderItem.miid=menuItem.miid group by orders.username; 

select name, balanceOwed from user where balanceOwed > 0;

select menuItem.name, menuItem.miid, menuItem.price, sum(ingredient.price) from menuItem inner join recipe on menuItem.miid=recipe.miid inner join ingredient on recipe.iid=ingredient.iid group by menuItem.miid order by menuItem.miid;
