from scoremodel.views.admin import admin
from flask import request, make_response, render_template, redirect, url_for, flash
from flask.ext.login import login_required
from scoremodel.modules.user.authentication import must_be_admin
from scoremodel.modules.api.report import ReportApi
from scoremodel.modules.api.answer import AnswerApi
from scoremodel.modules.api.risk_factor import RiskFactorApi
from scoremodel.modules.report.admin import ReportCreateForm, ReportDeleteForm
from scoremodel.modules.error import DatabaseItemAlreadyExists, RequiredAttributeMissing, DatabaseItemDoesNotExist
from flask.ext.babel import gettext as _


@admin.route('/reports', methods=['GET'])
@login_required
@must_be_admin
def v_report_list():
    a_report = ReportApi()
    l_reports = a_report.list()
    return render_template('admin/report/list.html', reports=l_reports)


@admin.route('/reports/id/<int:report_id>/edit', methods=['GET'])
@login_required
@must_be_admin
def v_report_edit(report_id):
    a_report = ReportApi()
    a_answer = AnswerApi()
    a_risk_factor = RiskFactorApi()
    try:
        existing_report = a_report.read(report_id)
    except DatabaseItemDoesNotExist:
        flash(_('No report with id {0} exists.').format(report_id))
        return redirect(url_for('admin.v_report_list'))
    return render_template('admin/report/edit_v2.html', report=existing_report, all_risk_factors=a_risk_factor.list(),
                           all_answers=a_answer.list())


@admin.route('/reports/id/<int:report_id>/delete', methods=['GET', 'POST'])
@login_required
@must_be_admin
def v_report_delete(report_id):
    form = ReportDeleteForm()
    a_report = ReportApi()
    try:
        existing_report = a_report.read(report_id)
    except DatabaseItemDoesNotExist:
        flash(_('No report with id {0} exists.').format(report_id))
        return url_for('admin.v_report_list')
    if request.method == 'POST' and form.validate_on_submit():
        try:
            if a_report.delete(report_id) is True:
                flash(_('Report {0} removed.').format(report_id))
            else:
                flash(_('Failed to remove report {0}.').format(report_id))
        except Exception as e:
            flash(_('An unexpected error occurred.'))
            return render_template('admin/generic/delete.html', action_url=url_for('admin.v_report_delete',
                                                                                   report_id=report_id),
                                   item_type=_('Report'), item_identifier=existing_report.title, form=form)
        else:
            return redirect(url_for('admin.v_report_list'))
    return render_template('admin/generic/delete.html', action_url=url_for('admin.v_report_delete',
                                                                           report_id=report_id),
                           item_type=_('Report'), item_identifier=existing_report.title, form=form)


@admin.route('/reports/create', methods=['GET', 'POST'])
@login_required
@must_be_admin
def v_report_create():
    form = ReportCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        a_report = ReportApi()
        input_data = {
            'title': form.title.data
        }
        try:
            new_report = a_report.create(input_data)
        except DatabaseItemAlreadyExists as e:
            flash(_('A report called {0} already exists.').format(input_data['title']))
            return render_template('admin/report/create.html', form=form)
        except RequiredAttributeMissing as e:
            flash(_('A required form element was not submitted: {0}').format(e))
            return render_template('admin/report/create.html', form=form)
        except Exception as e:  # Remove this after debugging
        #    flash('An unexpected error occurred: {0}'.format(e))
            flash(_('An unexpected error occurred.'))
            return render_template('admin/report/create.html', form=form)
        else:
            flash(_('Report created.'))
            return redirect(url_for('admin.v_report_edit', report_id=new_report.id))
    return render_template('admin/report/create.html', form=form)

##
# Helpers (TODO?)
##
