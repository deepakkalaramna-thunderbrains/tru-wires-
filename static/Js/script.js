//navbar active
document.querySelectorAll(".nav-link").forEach((link) => {
    if (link.href === window.location.href) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
    }
});

//navbar active end

// Date Selection Restriction
$(function() {
    $('[type="date"].min-today').prop("min", function() {
        return new Date().toJSON().split("T")[0];
    });
});
// Date Selection Restriction End

// Currency Feild Display
// function selectElement(id, valueToSelect) {
//     let element = document.getElementById(id);
//     element.value = valueToSelect;
// };

// function hideCurrencyFeild() {
//     domestic = document.getElementById("value_0");
//     $("#value_0").on("click", function() {
//         selectElement("select_currency_feild", "USD");
//         $(".ibank #require").remove();
//         $(
//             "#id_intermediary_bank_name,#id_intermediary_bank_st_adress,#id_intermediary_bank_country,#id_intermediary_bank_post_code"
//         ).removeAttr("required");
//         $("#currency_select_feild").hide();
//     });
// }

// document.addEventListener("DOMContentLoaded", hideCurrencyFeild);
// hideCurrencyFeild()

// function showCurrencyFeild() {
//     $("#value_1").on("click", function() {
//         $("#currency_select_feild").show();
//         selectElement("select_currency_feild", "---------");
//         $(
//             "#id_intermediary_bank_name,#id_intermediary_bank_st_adress,#id_intermediary_bank_country,#id_intermediary_bank_post_code"
//         ).attr("required", "required");
//         asterisk = '<span id="require">*</span>';
//         $(".ibank label").append(asterisk);
//     });
// }

// showCurrencyFeild()
// document.addEventListener("DOMContentLoaded", showCurrencyFeild);
// console.log("Test")
window.onload = function() { 
    
    var countryField = document.getElementById("intermediary_bank_country");
    var stateField = document.getElementById("id_intermediary_bank_state");
    //var countryNameField = document.getElementById("intermediary_bank_country_name");
    var ibStateContainerTwo = document.getElementById("ib_state_container2");
    //var ibStateContainer = document.getElementById("ib_state_container");
    countryField.onchange = (event) => {
	//alert("Changed: " + countryField.value);
        if (countryField.value === "USA") {
            stateField.style.display = "block";
            //countryNameField.style.display = "none"
	    //if(ibStateContainer !== undefined) ibStateContainer.style.display = "block";
	    if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "block";
		//alert("is uS");
        } else if (countryField.value === "OTHER") {
            stateField.style.display = "none";
	    //ibStateContainer.style.display = "none";
	    if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "none";
            countryNameField.style.display = "block";
        } else {
	    if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "none";
            stateField.style.display = "none";
	    //ibStateContainer.style.display = "none";
            countryNameField.style.display = "none";
        }
    }

    if (countryField.value === "USA") {
        stateField.style.display = "block";
	if(ibStateContainer !== undefined) ibStateContainer.style.display = "block";
        countryNameField.style.display = "none";
	if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "block";
    } else if (countryField.value === "OTHER") {
        if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "none";
        stateField.style.display = "none";
	if(ibStateContainer !== undefined) ibStateContainer.style.display = "none";
        countryNameField.style.display = "block";
    } else {
	if(ibStateContainerTwo !== undefined) ibStateContainerTwo.style.display = "none";
        stateField.style.display = "none";
	// if(ibStateContainer !== undefined) ibStateContainer.style.display = "none";
    //     countryNameField.style.display = "none";
    }

    /*countryField.onchange = (event) => {
	alert("Changed");
        if (countryField.value === "USA") {
            stateField.style.display = "block";
            countryNameField.style.display = "none";
        } else if (countryField.value === "OTHER") {
            stateField.style.display = "none";
            countryNameField.style.display = "block";
        } else {
            stateField.style.display = "none";
            countryNameField.style.display = "none";
        }
    };*/
};
// Country Feild Display End

// Currency Feild Display End

function selectElement(id, valueToSelect) {
    let element = document.getElementById(id);
    element.value = valueToSelect;
}

const currencyFeild = document.getElementById("currency_select_feild");
var domestic = document.getElementById("value_0");
var international = document.getElementById("value_1");
var ibankElements = document.querySelectorAll(".ibank");


function paymentCheck() {
    if (domestic.checked) {
        currencyFeild.style.display = "none";
        selectElement("select_currency_feild", "USD");
        $(
            "#id_intermediary_bank_name,#id_intermediary_bank_st_adress,#intermediary_bank_country,#intermediary_bank_state,#id_intermediary_bank_country_name,#id_intermediary_bank_post_code"
        ).removeAttr("required");
    } else if (international.checked) {
        currencyFeild.style.display = "block";
        $("#select_currency_feild").attr("required", true);
        $(
            "#id_intermediary_bank_name,#id_intermediary_bank_st_adress,#intermediary_bank_country,#intermediary_bank_state,#id_intermediary_bank_country_name,#id_intermediary_bank_post_code"
        ).attr("required", true);
    } else {
        currencyFeild.style.display = "none";
    }
}

function toggleAsterisk() {
    var domestic = document.getElementById("value_0").checked;
    var international = document.getElementById("value_1").checked;
    var ibankElements = document.querySelectorAll(".ibank");

    ibankElements.forEach(function(element) {
        if (domestic) {
            element.style.display = "none";
        } else if (international) {
            element.style.display = "inline";
        } else {
            element.style.display = "none";
        }
    });
}

function disableSubmitButton(){
    var button = document.getElementById("submitOrder");
    button.prop('disabled', true);
}

document.addEventListener("DOMContentLoaded", function() {
    document
        .querySelectorAll('input[name="destination"]')
        .forEach(function(el) {
            el.addEventListener("change", toggleAsterisk);
        });

    toggleAsterisk();
});

// Call the function on page load if needed
domestic.addEventListener("change", paymentCheck);
international.addEventListener("change", paymentCheck);
document.addEventListener("DOMContentLoaded", paymentCheck);
paymentCheck();
toggleAsterisk();

// Reccurency Feild Display
const selectReccuringFeild = document.getElementById("reccuringFeild");

var recurringCheckbox = document.getElementById("reccuringCheck");

function showHideRecurrence() {
    if (recurringCheckbox.checked) {
        selectReccuringFeild.style.display = "";
    } else {
        selectReccuringFeild.style.display = "none";
    }
}

if (recurringCheckbox) {
    recurringCheckbox.addEventListener("change", showHideRecurrence);
    document.addEventListener("DOMContentLoaded", showHideRecurrence);
    showHideRecurrence();
}


// Reccurency Feild Display End
// Country Feild Display 

// Reccurency Feild Required
// var recurringCheckbox = document.getElementById("reccuringCheck");
// const freqField = document.querySelector(".freq select");
// const limitField = document.querySelector(".limit input[type='checkbox']");

// recurringCheckbox.addEventListener("change", () => {
//     if (recurringCheckbox.checked) {
//         freqField.required = true;
//         limitField.required = true;
//     } else {
//         freqField.required = false;
//         limitField.required = false;
//     }
// });

// Reccurency Feild Required End


getPagination("#table-id");
$("#maxRows").trigger("change");

function getPagination(table) {
    $("#maxRows").on("change", function() {
        $(".pagination").html("");
        var trnum = 0;
        var maxRows = parseInt($(this).val());
        var totalRows = $(table + " tbody tr").length;
        $(table + " tr:gt(0)").each(function() {
            trnum++;
            if (trnum > maxRows) {
                $(this).hide();
            }
            if (trnum <= maxRows) {
                $(this).show();
            }
        });
        if (totalRows > maxRows) {
            var pagenum = Math.ceil(totalRows / maxRows);

            for (var i = 1; i <= pagenum;) {
                $(".pagination")
                    .append(
                        '<li data-page="' +
                        i +
                        '">\
								      <span>' +
                        i++ +
                        '<span class="sr-only">(current)</span></span>\
								    </li>'
                    )
                    .show();
            }
        }
        $(".pagination li:first-child").addClass("active");

        showig_rows_count(maxRows, 1, totalRows);

        $(".pagination li").on("click", function(e) {
            e.preventDefault();
            var pageNum = $(this).attr("data-page");
            var trIndex = 0;
            $(".pagination li").removeClass("active");
            $(this).addClass("active");

            showig_rows_count(maxRows, pageNum, totalRows);

            $(table + " tr:gt(0)").each(function() {
                trIndex++;

                if (
                    trIndex > maxRows * pageNum ||
                    trIndex <= maxRows * pageNum - maxRows
                ) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        });
    });
}

$(function() {
    default_index();
});

function showig_rows_count(maxRows, pageNum, totalRows) {
    var end_index = maxRows * pageNum;
    var start_index = maxRows * pageNum - maxRows + parseFloat(1);
    var string =
        "Showing " +
        start_index +
        " to " +
        end_index +
        " of " +
        totalRows +
        " entries";
    $(".rows_count").html(string);
}

function default_index() {
    $("table tr:eq(0)").prepend("<th> ID </th>");

    var id = 0;

    $("table tr:gt(0)").each(function() {
        id++;
        $(this).prepend("<td>" + id + "</td>");
    });
}

function FilterkeyWord_all_table() {
    var count = $(".table")
        .children("tbody")
        .children("tr:first-child")
        .children("td").length;

    var input, filter, table, tr, td, i;
    input = document.getElementById("search_input_all");
    var input_value = document.getElementById("search_input_all").value;
    filter = input.value.toLowerCase();
    if (input_value != "") {
        table = document.getElementById("table-id");
        tr = table.getElementsByTagName("tr");

        for (i = 1; i < tr.length; i++) {
            var flag = 0;

            for (j = 0; j < count; j++) {
                td = tr[i].getElementsByTagName("td")[j];
                if (td) {
                    var td_text = td.innerHTML;
                    if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
                        flag = 1;
                    } else {}
                }
            }
            if (flag == 1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    } else {
        $("#maxRows").trigger("change");
    }
}

$("#recurrencyDataCell").html();
