from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Post, Comment
from forms import RegisterForm, LoginForm, PostForm

def register_routes(app, login_manager):

    # -------------------- User Loader --------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "login"

    # -------------------- Home --------------------
    @app.route("/")
    def home():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("home.html", posts=posts)

    # -------------------- Register --------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        form = RegisterForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash("Username already exists. Please choose another.", "danger")
                return render_template("register.html", form=form)

            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        return render_template("register.html", form=form)

    # -------------------- Login --------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in successfully!", "success")
                return redirect(url_for("home"))
            flash("Invalid username or password", "danger")
        return render_template("login.html", form=form)

    # -------------------- Logout --------------------
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "success")
        return redirect(url_for("login"))

    # -------------------- Create Post --------------------
    @app.route("/create", methods=["GET", "POST"])
    @login_required
    def create_post():
        form = PostForm()
        if form.validate_on_submit():
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            flash("Post created successfully", "success")
            return redirect(url_for("home"))
        return render_template("create_post.html", form=form)

    # -------------------- Post Detail + Comment --------------------
    @app.route("/post/<int:post_id>", methods=["GET", "POST"])
    @login_required
    def post_detail(post_id):
        post = Post.query.get_or_404(post_id)

        if request.method == "POST":
            comment_content = request.form.get("comment")
            if comment_content:
                comment = Comment(content=comment_content, user_id=current_user.id, post_id=post.id)
                db.session.add(comment)
                db.session.commit()
                flash("Comment added!", "success")
            return redirect(url_for("post_detail", post_id=post_id))

        return render_template("post_detail.html", post=post)

    # -------------------- Like / Unlike Post --------------------
    @app.route("/like/<int:post_id>")
    @login_required
    def like_post(post_id):
        post = Post.query.get_or_404(post_id)
        if current_user in post.liked_by:
            post.liked_by.remove(current_user)
        else:
            post.liked_by.append(current_user)
        db.session.commit()
        return redirect(url_for("post_detail", post_id=post_id))

    # -------------------- Like / Unlike Comment --------------------
    @app.route("/like_comment/<int:comment_id>", methods=["POST"])
    @login_required
    def like_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        if current_user in comment.liked_by:
            comment.liked_by.remove(current_user)
        else:
            comment.liked_by.append(current_user)
        db.session.commit()
        return redirect(url_for("post_detail", post_id=comment.post_id))

    # -------------------- Delete Comment --------------------
    @app.route("/delete_comment/<int:comment_id>", methods=["POST"])
    @login_required
    def delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        if comment.user_id != current_user.id:
            flash("You cannot delete this comment.", "danger")
            return redirect(url_for("post_detail", post_id=comment.post_id))
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted!", "success")
        return redirect(url_for("post_detail", post_id=comment.post_id))