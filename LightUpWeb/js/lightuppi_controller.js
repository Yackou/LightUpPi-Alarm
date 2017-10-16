/**
 * @license Licensed under the Apache License, Version 2.0 (the "License"):
 *          http://www.apache.org/licenses/LICENSE-2.0
 *
 * @fileoverview LightUpPi app AngularJS controller.
 */
"use strict";

/** Create/reuse the namespace for the application and Angular app. */
var LightUpPi = LightUpPi || {};
LightUpPi.app = angular.module("lightUpPi", ["ui.bootstrap"]);

/**
 * Main controller for the LightUpPi Angular App.
 * It sets short polling to the server to maintain the displayed alarm data 
 * refreshed.
 */
LightUpPi.app.controller("lightUpCtrl", ["$scope", "$interval", "$http",
    function($scope, $interval, $http) {
  $scope.serverError = false;
  $scope.serverStationError = false;
  $scope.alarms = [];
  $scope.stations = [];

  $scope.refreshAlarmsData = function() {
    $http.get("/LightUpPi/getAlarm?id=all")
         .success(function(data) {
           if (typeof data.error == 'undefined') {
             $scope.alarms = data.alarms;
             $scope.serverError = false;
           } else {
             $scope.alarms = LightUpPi.demoAlarms;
             $scope.serverError = true;
           }
         })
         .error(function(data, status) {
           $scope.alarms = LightUpPi.demoAlarms;
           $scope.serverError = true;
         });
  };

    $scope.refreshStationsData = function() {
    $http.get("/LightUpPi/getStation?id=all")
         .success(function(data) {
           if (typeof data.error == 'undefined') {
             $scope.stations = data.stations;
             $scope.serverStationError = false;
           } else {
             $scope.serverStationError = true;
           }
         })
         .error(function(data, status) {
           $scope.serverStationError = true;
         });
  };

  $scope.refreshAlarmsData();
  $scope.refreshStationsData();
//  var promise = $interval($scope.refreshAlarmsData, 2000);
}]);

/**
 * This controls the Modal launched to add a new alarm. It only controls the
 * modal execution, code within the modal is connected in 'AddAlarmCtrl'.
 */
LightUpPi.app.controller("AddAlarmModalCtrl", ["$scope", "$modal", "$log",
    function ($scope, $modal, $log) {
  $scope.animationsEnabled = true;

  $scope.open = function (size) {
    var modalInstance = $modal.open({
      scope: $scope,
      animation: $scope.animationsEnabled,
      templateUrl: "addalarm.html",
      controller: "AddAlarmCtrl",
      size: size,
      resolve: {
        items: function () {
          return $scope.items;
        }
      }
    });

    modalInstance.result.then(
      function (selectedItem) {
        $scope.selected = selectedItem;
      },
      function () {
        $log.info("Modal dismissed at: " + new Date());
      }
    );
  };
}]);

/**
 * Mote that $modalInstance represents a modal window (instance) dependency. It
 * is not the same as the $modal service used in AddAlarmModalCtrl.
 */
LightUpPi.app.controller("AddAlarmCtrl", ["$scope", "$modalInstance", "$log", "$http",
    function ($scope, $modalInstance, $log, $http) {
  $scope.ok = function () {
    $scope.addAlarm = function() {
    $http.get("/LightUpPi/addAlarm?hour=" + $scope.mytime.getHours() +
              "&minute=" + $scope.mytime.getMinutes() +
              "&monday=" + $scope.monday +
              "&tuesday=" + $scope.tuesday +
              "&wednesday=" + $scope.wednesday +
              "&thursday=" + $scope.thursday +
              "&friday=" + $scope.friday +
              "&saturday=" + $scope.saturday +
              "&sunday=" + $scope.sunday +
              "&label=" + $scope.label)
         .success(function(data) {
           if (typeof data.error == 'undefined') {
             $scope.serverError = false;
             $scope.refreshAlarmsData();
           } else {
             $scope.serverError = true;
           }
         })
         .error(function(data, status) {
           $scope.serverError = true;
         });
    };
    $log.log("Adding alarm: " + $scope.mytime.getHours() + $scope.mytime.getMinutes());
    $scope.addAlarm();
    $modalInstance.close();
  };

  $scope.cancel = function () {
    $modalInstance.dismiss("cancel");
  };

  $scope.mytime = new Date();
  $scope.hstep = 1;
  $scope.mstep = 1;

  $scope.monday = false;
  $scope.tuesday = false;
  $scope.wednesday = false;
  $scope.thursday = false;
  $scope.friday = false;
  $scope.saturday = false;
  $scope.sunday = false;

  $scope.label = "";

  $scope.ismeridian = true;
  $scope.toggleMeridianMode = function() {
    $scope.ismeridian = ! $scope.ismeridian;
  };

  $scope.changed = function () {
    $log.log("Time changed to: " + $scope.mytime);
  };
}]);

/**
 * Controller for the navigation bar drop down which allows dynamic theme
 * selection.
 */
LightUpPi.app.controller("ThemeDropdownCtrl", ["$scope", "$log", "$location",
    function ($scope, $log, $location) {
  this.themeCssFiles = LightUpPi.themeList;

  this.editCssTheme = function(themeName, cssFile) {
    LightUpPi.editCssTheme(cssFile);
    // Edit the address bar location without reloading the page
    $location.url("/?theme=" + themeName).replace();
  };

  $scope.status = {
    isopen: false
  };

  $scope.toggled = function(open) {
    $log.log("Dropdown is now: ", open);
  };

  $scope.toggleDropdown = function($event) {
    $event.preventDefault();
    $event.stopPropagation();
    $scope.status.isopen = !$scope.status.isopen;
  };
}]);

/**
 * Controller for the Alarm Panels. It collects the JSON data from the server
 * and creates a panel per Alarm with all its information.
 */
LightUpPi.app.controller("AlarmPanelController", ["$scope", "$http",
    function ($scope, $http) {
  var context = this;
  this.showTimestamp = true;

  // Returns a string to indicate if the alarm is enabled or disabled
  this.enabledButtonText = function(enabled) {
    if (enabled) {
      return "Enabled";
    } else {
      return "Disabled";
    }
  };

  this.enabledButtonClick = function(id, enabled) {
    $http.get("/LightUpPi/editAlarm?id=" + id +
              "&enabled=" + !enabled)
         .success(function(data) { $scope.refreshAlarmsData(); });
  }

  this.deleteButtonClick = function(id) {
    $http.get("/LightUpPi/deleteAlarm?id=" + id)
         .success(function(data) { $scope.refreshAlarmsData(); });
  }

  // Formats a string to list the repeat days
  this.formatedRepeat = function(alarm) {
    var d = "---"
    var strArray = [];
    if (alarm.monday)    { strArray.push("Mon"); } else { strArray.push(d); }
    if (alarm.tuesday)   { strArray.push("Tue"); } else { strArray.push(d); }
    if (alarm.wednesday) { strArray.push("Wed"); } else { strArray.push(d); }
    if (alarm.thursday)  { strArray.push("Thu"); } else { strArray.push(d); }
    if (alarm.friday)    { strArray.push("Fri"); } else { strArray.push(d); }
    if (alarm.saturday)  { strArray.push("Sat"); } else { strArray.push(d); }
    if (alarm.sunday)    { strArray.push("Sun"); } else { strArray.push(d); }
    return strArray.join(" ");
  };
}]);



/**
 * Controller for the Station Table. It collects the JSON data from the server
 * and creates a row per Station with all its information.
 */
LightUpPi.app.controller("StationController", ["$scope", "$http", "$log",
    function ($scope, $http, $log) {
  var context = this;

  this.addButtonClick = function() {
    $scope.addStation = function() {
    $http.get("/LightUpPi/addStation?name=" + $scope.new_station_name +
              "&url=" + $scope.new_station_url)
         .success(function(data) {
            $scope.new_station_name = ""
            $scope.new_station_url = ""
            $scope.refreshStationsData();
            $log.info("Station added: " + $scope.new_station_name + " " + $scope.new_station_url);
         })
         .error(function(data, status) {
           $scope.serverStationError = true;
           $log.info("Error adding Station: " + $scope.new_station_name + " " + $scope.new_station_url);
         });
    };
    $log.info("Adding Station: " + $scope.new_station_name + " " + $scope.new_station_url);
    $scope.addStation();
  };

  this.deleteButtonClick = function(id) {
    $http.get("/LightUpPi/deleteStation?id=" + id)
         .success(function(data) { $scope.refreshStationsData(); });
  };

  $scope.new_station_name = "";
  $scope.new_station_url = "";

}]);



/**
 * Create a custom filter to always display a leading zero for < 10 digits.
 * Useful for time display.
 */
LightUpPi.app.filter("leadingzero", function() {
  return function(input) {
    if (input < 10) { 
      input = "0" + input;
    }
    return input;
  };
});

/** Default Alarm JSON array for demo shown on server error. */
LightUpPi.demoAlarms = [
  {
    "saturday": false,
    "monday": true,
    "timestamp": 1431391253,
    "tuesday": true,
    "friday": true,
    "id": 1,
    "minute": 30,
    "hour": 7,
    "enabled": true,
    "wednesday": true,
    "thursday": true,
    "label": "Fake default alarm 1",
    "sunday": false
  },
  {
    "saturday": true,
    "monday": false,
    "timestamp": 1431211548,
    "tuesday": false,
     "friday": false,
    "id": 2,
    "minute": 45,
    "hour": 10,
    "enabled": true,
    "wednesday": false,
    "thursday": false,
    "label": "Fake default alarm 2",
    "sunday": true
  }
];
