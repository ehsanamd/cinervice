from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import Movie, Series, People, Cinema, Role, Contact_Form, Movies_Vote, Series_Vote, Cinema_Vote, People_Vote
from news.models import New
from django.db.models import Avg, Count
from itertools import chain
from django.views.decorators.csrf import csrf_exempt


def index(request):
    if(request.user.is_authenticated):
        # Estimate average of user votes
        rate_avg_movie = Movies_Vote.objects.filter(
            user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
        rate_avg_serial = Series_Vote.objects.filter(
            user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
        rate_avg_people = People_Vote.objects.filter(
            user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
        rate_avg_cinema = Cinema_Vote.objects.filter(
            user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')

        cinema_in_slider_by_movie = []
        cinema_in_slider_by_people = []
        cinema_in_slider_by_serial = []

        if(rate_avg_movie is not None or rate_avg_serial is not None or
           rate_avg_people is not None or rate_avg_cinema is not None):
            if(rate_avg_movie is None):
                rate_avg_movie = 0
            if(rate_avg_serial is None):
                rate_avg_serial = 0
            if(rate_avg_people is None):
                rate_avg_people = 0
            if(rate_avg_cinema is None):
                rate_avg_cinema = 0

            # Suggest By Vote to The People

            # fetch all popular people
            all_fav_people = People_Vote.objects.filter(
                vote__gte=rate_avg_people, user_id=request.user.id)

            for i in all_fav_people:
                # fetch all role of popular people
                all_role_of_fav_people = Role.objects.filter(
                    person=i.people_id)

                for ii in all_role_of_fav_people:
                    # filter popular movie of popular people
                    fav_movie_filtered = Movies_Vote.objects.filter(
                        movie=ii.movie_id, user_id=request.user.id).exclude(vote__lte=rate_avg_movie)

                    for iii in fav_movie_filtered:
                        # fetch all role in popular movie
                        all_role_in_fav_movie_by_people = Role.objects.filter(
                            movie=iii.movie_id)
                        sum_rate_of_people_in_movie = 0

                        # calculate average rate of popular movie
                        for calc in all_role_in_fav_movie_by_people:
                            try:
                                sum_rate_of_people_in_movie += People_Vote.objects.filter(people=calc.person_id,
                                                                                          user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
                            except:
                                sum_rate_of_people_in_movie = 0
                        avg_rate_of_people_in_movie = sum_rate_of_people_in_movie / \
                            all_role_in_fav_movie_by_people.count()

                        # filter people that less than average rate
                        if avg_rate_of_people_in_movie >= rate_avg_people:
                            for iv in all_role_in_fav_movie_by_people:
                                # fetch all cinema by fav movie
                                cinema_by_filtered_movie = Cinema.objects.filter(
                                    movie=iv.movie_id)

                                for v in cinema_by_filtered_movie:
                                    # filter cinema by average vote
                                    fav_cinema = Cinema_Vote.objects.filter(
                                        user_id=request.user.id, cinema=v.id).exclude(vote__lt=rate_avg_cinema)

                                    for vi in fav_cinema:
                                        # fetch cinema filtered
                                        filtered_cinema = Cinema.objects.filter(
                                            id=vi.cinema_id)
                                        for j in filtered_cinema:
                                            cinema_in_slider_by_people.append(
                                                j)

            # Suggest By Vote to The Movie(people are same)

            # fetch all popular movie
            all_fav_movie = Movies_Vote.objects.filter(
                vote__gte=rate_avg_movie, user_id=request.user.id)
            
            for i in all_fav_movie:
                # fetch all role in popular movie
                all_role_in_fav_movie = Role.objects.filter(movie=i.movie_id)

                for ii in all_role_in_fav_movie:

                    # find unpopular people
                    unpopular_people = People_Vote.objects.filter(
                        user_id=request.user.id, people=ii.person_id, vote__lte=rate_avg_people)

                    for ix in unpopular_people:

                        # fetch unpopular people
                        fetch_unpopular_people = Role.objects.filter(
                            person=ix.people_id)

                        # remove unpopular role
                        all_role_in_fav_movie = all_role_in_fav_movie.difference(
                            fetch_unpopular_people)

                        for ixi in all_role_in_fav_movie:

                            # fetch all movie of best role
                            all_movie_of_best_role = Role.objects.filter(
                                person=ixi.person_id, type_of_product='M')

                            for ixii in all_movie_of_best_role:
                                    
                                # find unpopular movie
                                unpopular_movie = Movies_Vote.objects.filter(
                                    user_id=request.user.id, movie=ixii.movie_id, vote__lte=rate_avg_movie)
                                for aux in unpopular_movie:

                                    # fetch unpopular movie
                                    fetch_unpopular_movie = Role.objects.filter(movie=aux.movie_id)
                                    
                                    # remove unpopular movie
                                    all_movie_of_best_role = all_movie_of_best_role.difference(fetch_unpopular_movie)

                                    # fetch all role in popular movie   
                                    sum_rate_of_people_in_movie = 0

                                    # calculate average rate of popular movie
                                    for calc in all_movie_of_best_role:
                                        try:
                                            sum_rate_of_people_in_movie += People_Vote.objects.filter(people=calc.person_id,
                                                                                                        user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
                                        except:
                                            sum_rate_of_people_in_movie = 0
                                    if all_movie_of_best_role.count() != 0:
                                        avg_rate_of_people_in_movie = sum_rate_of_people_in_movie / \
                                            all_movie_of_best_role.count()
                                    # filter people that less than average rate
                                    if avg_rate_of_people_in_movie >= rate_avg_people:

                                        for iv in all_movie_of_best_role:

                                            # fetch all cinema by fav movie
                                            cinema_by_filtered_movie = Cinema.objects.filter(
                                                movie=iv.movie_id)

                                            for v in cinema_by_filtered_movie:

                                                # find unpopular cinema
                                                unpopular_cinema = Cinema_Vote.objects.filter(
                                                    user_id=request.user.id, cinema_id=v.id, vote__lte=rate_avg_cinema)

                                                for vi in unpopular_cinema:
                                                    print(vi.cinema)
                                                    # fetch unpopular cinema
                                                    fetch_unpopular_cinema = Cinema.objects.filter(
                                                        id=vi.cinema_id)

                                                    cinema_by_filtered_movie = cinema_by_filtered_movie.difference(
                                                        fetch_unpopular_cinema)

                                                    for j in cinema_by_filtered_movie:
                                                        # append cinema filtered
                                                        cinema_in_slider_by_movie.append(
                                                            j)

            # Suggest By Vote to The Serial(people are same)

            # fetch all popular serial
            all_fav_serial = Series_Vote.objects.filter(
                vote__gte=rate_avg_serial, user_id=request.user.id)

            for i in all_fav_serial:
                # fetch all role in popular serial
                all_role_in_fav_serial = Role.objects.filter(
                    serial=i.serial_id)

                for ii in all_role_in_fav_serial:

                    # find unpopular people
                    unpopular_people = People_Vote.objects.filter(
                        user_id=request.user.id, people=ii.person_id, vote__lte=rate_avg_people)

                    for ix in unpopular_people:

                        # fetch unpopular people
                        fetch_unpopular_people = Role.objects.filter(
                            person=ix.people_id)

                        # remove unpopular role
                        all_role_in_fav_serial = all_role_in_fav_serial.difference(
                            fetch_unpopular_people)

                        for ixi in all_role_in_fav_serial:

                             # find unpopular movie
                                unpopular_movie = Movies_Vote.objects.filter(
                                    user_id=request.user.id, movie=ixii.movie_id, vote__lte=rate_avg_movie)
                                for aux in unpopular_movie:

                                    # fetch unpopular movie
                                    fetch_unpopular_movie = Role.objects.filter(movie=aux.movie_id)
                                    
                                    # remove unpopular movie
                                    all_movie_of_best_role = all_movie_of_best_role.difference(fetch_unpopular_movie)

                                    # fetch all role in popular movie   
                                    sum_rate_of_people_in_movie = 0

                                    # calculate average rate of popular movie
                                    for calc in all_movie_of_best_role:
                                        try:
                                            sum_rate_of_people_in_movie += People_Vote.objects.filter(people=calc.person_id,
                                                                                                        user_id=request.user.id).aggregate(Avg('vote')).get('vote__avg')
                                        except:
                                            sum_rate_of_people_in_movie = 0
                                    if all_movie_of_best_role.count() != 0:
                                        avg_rate_of_people_in_movie = sum_rate_of_people_in_movie / \
                                            all_movie_of_best_role.count()
                                    # filter people that less than average rate
                                    if avg_rate_of_people_in_movie >= rate_avg_people:

                                        for iv in all_movie_of_best_role:

                                            # fetch all cinema by fav movie
                                            cinema_by_filtered_movie = Cinema.objects.filter(
                                                movie=iv.movie_id)

                                            for v in cinema_by_filtered_movie:

                                                # find unpopular cinema
                                                unpopular_cinema = Cinema_Vote.objects.filter(
                                                    user_id=request.user.id, cinema_id=v.id, vote__lte=rate_avg_cinema)

                                                for vi in unpopular_cinema:
                                                    print(vi.cinema)
                                                    # fetch unpopular cinema
                                                    fetch_unpopular_cinema = Cinema.objects.filter(
                                                        id=vi.cinema_id)

                                                    cinema_by_filtered_movie = cinema_by_filtered_movie.difference(
                                                        fetch_unpopular_cinema)

                                                    for j in cinema_by_filtered_movie:
                                                        # append cinema filtered
                                                        cinema_in_slider_by_serial.append(
                                                            j)

            cinema_in_slider = list(chain(
                cinema_in_slider_by_movie, cinema_in_slider_by_people, cinema_in_slider_by_serial))
            print(len(cinema_in_slider))
            # if can't find any cinema by votes
            if len(cinema_in_slider) == 0:
                fav_cinema = Cinema_Vote.objects.filter(
                    user_id=request.user.id).exclude(vote__lt=rate_avg_cinema)
                for j in fav_cinema:
                    cinema = list(
                        Cinema.objects.filter(id=j.cinema_id))
                    for jj in cinema:
                        cinema_in_slider.append(jj)

        else:
            cinema_in_slider_by_movie = Cinema.objects.all()[:3]
            cinema_in_slider_by_people = Cinema.objects.all()[:3]
            cinema_in_slider_by_serial = Cinema.objects.all()[:3]
            cinema_in_slider = Cinema.objects.all()[:3]

    # NONE Suggestion
    else:
        cinema_in_slider_by_movie = Cinema.objects.all()[:3]
        cinema_in_slider_by_people = Cinema.objects.all()[:3]
        cinema_in_slider_by_serial = Cinema.objects.all()[:3]
        cinema_in_slider = Cinema.objects.all()[:3]

    news_in_index = New.objects.all()[:5]
    context = {
        'cinema_in_slider': cinema_in_slider,
        'news_in_index': news_in_index,
        'cinema_by_fav_movie': cinema_in_slider_by_movie,
        'cinema_by_fav_serial': cinema_in_slider_by_people,
        'cinema_by_fav_people': cinema_in_slider_by_serial,
    }
    # print(context)
    # print(cinema_in_slider)
    return render(request, 'index.html', context)

# Start of Movie Part Methods


def movies(request):
    movie_list = Movie.objects.all()
    paginator = Paginator(movie_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'movies/list.html', {'page_obj': page_obj})


def movie_info(request, movie_id):
    try:
        movie_info = Movie.objects.filter(pk=movie_id)
        count = Movies_Vote.objects.filter(movie_id=movie_id).count()
        rate = Movies_Vote.objects.filter(
            movie_id=movie_id).aggregate(Avg('vote')).get('vote__avg')
        if(rate is not None):
            rate = round(rate, 2)
        actors = Role.objects.all().filter(movie_id=movie_id, type_of_role='A')
        directors = Role.objects.all().filter(movie_id=movie_id, type_of_role='D')
        writers = Role.objects.all().filter(movie_id=movie_id, type_of_role='W')
        cinemas = Cinema.objects.all().filter(movie=movie_id)
    except Movie.DoesNotExist:
        raise Http404("Movie does not exist")
    return render(request, 'movies/info.html', {
        'info': movie_info,
        'count': count,
        'rate': rate,
        'actors': actors,
        'directors': directors,
        'writers': writers,
        'cinemas': cinemas,
    })


@ csrf_exempt
def movie_rate(request):
    if request.method == "POST":
        if(request.user.is_authenticated):
            vote = int(request.POST.get('point'))
            try:
                is_voted = Movies_Vote.objects.get(
                    movie_id=request.POST.get('movie-id'), user_id=request.user.id)
                if(is_voted is not None):
                    if(1 > vote or vote > 10):
                        return HttpResponse('Your vote is out of range')
                    else:
                        Movies_Vote.objects.filter(movie_id=request.POST.get(
                            'movie-id'), user_id=request.user.id).update(vote=vote)
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:
                if(1 > vote or vote > 10):
                    return HttpResponse('Your vote is out of range')
                else:
                    vote_object = Movies_Vote(vote=vote, movie_id=request.POST.get(
                        'movie-id'), user_id=request.user.id)
                    vote_object.save()
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponse('Please Login!')
    else:
        return HttpResponse('Invalid request')
# End of Movie Part Methods

# Start of TV Shows Part Methods


def series(request):
    series_list = Series.objects.all()
    paginator = Paginator(series_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'series/list.html', {'page_obj': page_obj})


def seri_info(request, seri_id):
    try:
        seri_info = Series.objects.filter(pk=seri_id)
        count = Series_Vote.objects.filter(serial_id=seri_id).count()
        rate = Series_Vote.objects.filter(
            serial_id=seri_id).aggregate(Avg('vote')).get('vote__avg')
        if(rate is not None):
            rate = round(rate, 2)
        actors = Role.objects.all().filter(serial_id=seri_id, type_of_role='A')
        directors = Role.objects.all().filter(serial_id=seri_id, type_of_role='D')
        writers = Role.objects.all().filter(serial_id=seri_id, type_of_role='W')
    except Series.DoesNotExist:
        raise Http404("TV Show does not exist")
    return render(request, 'series/info.html', {
        'info': seri_info,
        'count': count,
        'rate': rate,
        'actors': actors,
        'directors': directors,
        'writers': writers,
    })


@ csrf_exempt
def seri_rate(request):
    if request.method == "POST":
        if(request.user.is_authenticated):
            vote = int(request.POST.get('point'))
            try:
                is_voted = Series_Vote.objects.get(
                    serial_id=request.POST.get('serial-id'), user_id=request.user.id)
                if(is_voted is not None):
                    if(1 > vote or vote > 10):
                        return HttpResponse('Your vote is out of range')
                    else:
                        Series_Vote.objects.filter(serial_id=request.POST.get(
                            'serial-id'), user_id=request.user.id).update(vote=vote)
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:
                if(1 > vote or vote > 10):
                    return HttpResponse('Your vote is out of range')
                else:
                    vote_object = Series_Vote(vote=vote, serial_id=request.POST.get(
                        'serial-id'), user_id=request.user.id)
                    vote_object.save()
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponse('Please Login!')
    else:
        return HttpResponse('Invalid request')

# End of TV Shows Part Methods

# Start of Celebrity Part Methods


def people(request):
    people_list = People.objects.all()
    paginator = Paginator(people_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'peoples/list.html', context)


def people_info(request, people_id):
    try:
        people_info = People.objects.filter(pk=people_id)
        count = People_Vote.objects.filter(people_id=people_id).count()
        rate = People_Vote.objects.filter(
            people_id=people_id).aggregate(Avg('vote')).get('vote__avg')
        if(rate is not None):
            rate = round(rate, 2)
        movies = Role.objects.all().filter(person_id=people_id, type_of_product='M')
        series = Role.objects.all().filter(person_id=people_id, type_of_product='S')
        print(series)
        context = {
            'info': people_info,
            'count': count,
            'rate': rate,
            'movies': movies,
            'series': series,
        }
    except People.DoesNotExist:
        raise Http404("People does not exist")
    return render(request, 'peoples/info.html', context)


@csrf_exempt
def people_rate(request):
    if request.method == "POST":
        if(request.user.is_authenticated):
            vote = int(request.POST.get('point'))
            try:
                is_voted = People_Vote.objects.get(
                    people_id=request.POST.get('people-id'), user_id=request.user.id)
                if(is_voted is not None):
                    if(1 > vote or vote > 10):
                        return HttpResponse('Your vote is out of range')
                    else:
                        People_Vote.objects.filter(people_id=request.POST.get(
                            'people-id'), user_id=request.user.id).update(vote=vote)
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            except:
                if(1 > vote or vote > 10):
                    return HttpResponse('Your vote is out of range')
                else:
                    vote_object = People_Vote(vote=vote, people_id=request.POST.get(
                        'people-id'), user_id=request.user.id)
                    vote_object.save()
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponse('Please Login!')
    else:
        return HttpResponse('Invalid request')

# End of Celebrity Part Methods

# Start of Movie Theater Part Methods


def cinemas(request):
    cinema_list = Cinema.objects.all()
    paginator = Paginator(cinema_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'cinemas/list.html', context)


def cinema_info(request, cinema_id):
    try:
        cinema_info = Cinema.objects.filter(pk=cinema_id)
        count = Cinema_Vote.objects.filter(cinema_id=cinema_id).count()
        rate = Cinema_Vote.objects.filter(
            cinema_id=cinema_id).aggregate(Avg('vote')).get('vote__avg')
        if(rate is not None):
            rate = round(rate, 2)
    except Cinema.DoesNotExist:
        raise Http404("Movie Theater does not exist")
    return render(request, 'cinemas/info.html', {'info': cinema_info, 'count': count, 'rate': rate})


@csrf_exempt
def cinema_rate(request):
    if request.method == "POST":
        if(request.user.is_authenticated):
            vote = int(request.POST.get('point'))
            try:
                is_voted = Cinema_Vote.objects.get(
                    cinema_id=request.POST.get('cinema-id'), user_id=request.user.id)
                if(is_voted is not None):
                    if(1 > vote or vote > 10):
                        return HttpResponse('Your vote is out of range')
                    else:
                        Cinema_Vote.objects.filter(cinema_id=request.POST.get(
                            'cinema-id'), user_id=request.user.id).update(vote=vote)
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except:
                if(1 > vote or vote > 10):
                    return HttpResponse('Your vote is out of range')
                else:
                    vote_object = Cinema_Vote(vote=vote, cinema_id=request.POST.get(
                        'cinema-id'), user_id=request.user.id)
                    vote_object.save()
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponse('Please Login!')
    else:
        return HttpResponse('Invalid request')
# End of Movie Theater Part Methods

# About Part Method


def about(request):
    return render(request, 'about.html')

# Contact Part Method


@csrf_exempt
def contact(request):
    if request.method == "GET":
        return render(request, 'contact.html')

    elif request.method == "POST":
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        contact_form = Contact_Form(
            email=email, subject=subject)
        contact_form.save()

        return render(request, 'contact.html', {'situation': 'Your form has been received!'})

    else:
        return render(request, 'contact.html', {'situation': 'Invalid request!'})


def location(request):
    conetxt = {'latitude': 'bullshit'}
    print(request.POST)
    return render(request, 'location_sender.html', conetxt)
