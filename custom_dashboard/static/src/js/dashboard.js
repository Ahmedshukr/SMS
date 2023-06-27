odoo.define('custom_dashboard.dashboard_action', function (require){
"use strict";
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var CustomDashBoard = AbstractAction.extend({
   template: 'CustomDashBoard',

   init: function(parent, context) {
       this._super(parent, context);
       this.dashboards_templates = ['DashboardStudent', 'GenderDistribution'];
       this.today_sale = [];
   },
       willStart: function() {
       var self = this;
       return $.when(ajax.loadLibs(this), this._super()).then(function() {
           return self.fetch_data();
       });
   },
   start: function() {
            var self = this;
            this._super.apply(this, arguments);
            rpc.query({
                model: 'student.info',
                method: 'get_student_stats'
            }).then(function(result) {
                self.render_dashboards();
                self.render_pie_chart(result.gender_data);
                self.render_bar_chart1(result.standard_student_count);
                self.render_bar_chart2(result.academic_year_student_count);
            });
        },
//   start: function() {
//           var self = this;
//           this.set("title", 'Dashboard');
//           return this._super().then(function() {
//               self.render_dashboards();
//               self.render_pie_chart(result.gender_data);
//           });
//       },
       render_dashboards: function(){
       var self = this;
       _.each(this.dashboards_templates, function(template) {
               self.$('.o_pj_dashboard').append(QWeb.render(template, {widget: self}));
           });
   },

fetch_data: function() {
        var self = this;
        var def = this._rpc({
                model: 'student.info',
                method: 'get_student_stats'
    }).then(function(result) {
        self.total_students = result['total_students'];
        self.male_students = result['male_students'];
        self.female_students = result['female_students'];
        self.total_alumni = result['total_alumni'];
    });
    return $.when(def);
   },

   render_pie_chart: function(data) {
            var genderData = {
                datasets: [{
                    data: [data.male, data.female],
                    backgroundColor: ['#007bff', '#dc3545']
                }],
                labels: ['Male', 'Female']
            };
            var genderOptions = {
                responsive: true,
                maintainAspectRatio: false
            };
            var genderPieChart = new Chart(this.$('#gender_pie_chart'), {
                type: 'doughnut',
                data: genderData,
                options: genderOptions
            });
        },
        render_bar_chart1: function(data) {
    var labels = [], values = [];
    data.forEach(function(item) {
        labels.push(item[0]);
        values.push(item[1]);
    });
    var barData = {
        labels: labels,
        datasets: [{
            label: 'Student Count',
            backgroundColor: '#007bff',
            data: values
        }]
    };
    var barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    };
    var barChart = new Chart(this.$('#school_standards_bar_chart'), {
        type: 'bar',
        data: barData,
        options: barOptions
    });
},

render_bar_chart2: function(data) {
    var labels = [], values = [];
    data.forEach(function(item) {
        labels.push(item[0]);
        values.push(item[1]);
    });
    var barData = {
        labels: labels,
        datasets: [{
            label: 'Student Count',
            borderColor: '#9C27B0',
            data: values
        }]
    };
    var barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    };
    var barChart = new Chart(this.$('#academic_year_bar_chart'), {
        type: 'line',
        data: barData,
        options: barOptions
    });
},

})
core.action_registry.add('custom_dashboard_tags', CustomDashBoard);
return CustomDashBoard;
})