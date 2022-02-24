create table users
(
    id       serial primary key,
    username text,
    pass     text
);

create type song_diff as
(
    difficulty text,
    chart text,
    charter text
);

create type albumart as
(
    image text,
    artist text
);

create table songs
(
    id          serial primary key,
    song_name    text,
    author      text,
    easy_diff   song_diff,
    normal_diff song_diff,
    hard_diff   song_diff,
    song_art    albumart,
    music   text,
    uploader    integer,
    constraint  fk_user foreign key(uploader) references users(id)
);

create table favs
(
    user_id integer,
    song_id integer,
    constraint pk_favs primary key (user_id, song_id),
    constraint fk_user_fav foreign key(user_id) references users(id),
    constraint fk_song_fav foreign key(song_id) references songs(id)
)