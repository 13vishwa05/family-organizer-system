from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FamilyGroup, FamilyMembership, FamilyMember
from .forms import FamilyMemberForm, FamilyGroupForm

@login_required
def create_family_group(request):
    if request.method == 'POST':
        form = FamilyGroupForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            family.created_by = request.user
            family.save()
            FamilyMembership.objects.create(user=request.user, family_group=family, role='ADMIN')
            return redirect('families:family_members_list', family_id=family.id)
    else:
        form = FamilyGroupForm()
    return render(request, 'families/family_member_form.html', {'form': form, 'create_group': True})

@login_required
def family_members_list(request, family_id=None):
    # simple approach: use the first family of the user if none provided
    if family_id is None:
        family = request.user.family_groups.first()
    else:
        family = get_object_or_404(FamilyGroup, id=family_id)
    members = family.family_members.all() if family else []
    return render(request, 'families/family_members_list.html', {'family': family, 'members': members})

@login_required
def family_member_create(request, family_id):
    family = get_object_or_404(FamilyGroup, id=family_id)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            fm = form.save(commit=False)
            fm.family_group = family
            fm.save()
            return redirect('families:family_members_list', family_id=family.id)
    else:
        form = FamilyMemberForm()
    return render(request, 'families/family_member_form.html', {'form': form, 'family': family})

@login_required
def family_member_edit(request, family_id, member_id):
    family = get_object_or_404(FamilyGroup, id=family_id)
    member = get_object_or_404(FamilyMember, id=member_id, family_group=family)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('families:family_members_list', family_id=family.id)
    else:
        form = FamilyMemberForm(instance=member)
    return render(request, 'families/family_member_form.html', {'form': form, 'family': family, 'member': member})

@login_required
def family_member_delete(request, family_id, member_id):
    family = get_object_or_404(FamilyGroup, id=family_id)
    member = get_object_or_404(FamilyMember, id=member_id, family_group=family)
    if request.method == 'POST':
        member.delete()
        return redirect('families:family_members_list', family_id=family.id)
    return render(request, 'families/family_member_form.html', {'form': None, 'family': family, 'member': member, 'delete': True})
