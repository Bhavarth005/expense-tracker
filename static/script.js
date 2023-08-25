function formatDate(input) {
    console.log(input);
    const monthAbbreviations = {
        JAN: 'January',
        FEB: 'February',
        MAR: 'March',
        APR: 'April',
        MAY: 'May',
        JUN: 'June',
        JUL: 'July',
        AUG: 'August',
        SEP: 'September',
        OCT: 'October',
        NOV: 'November',
        DEC: 'December'
    };

    const parts = input.split('_');
    const monthAbbreviation = parts[0];
    const year = parts[1];

    const fullMonth = monthAbbreviations[monthAbbreviation];

    if (fullMonth) {
        return `${fullMonth}, 20${year}`;
    } else {
        return 'Invalid input';
    }
}

function createElementWithClassName(tag, className){
    let element = document.createElement(tag);
    element.className = className;
    return element;
}

function getSelectOption(text){
    let option = document.createElement("option");
    option.value = text;
    option.innerText = text;
    return option;
}

class Expense{
    static expenseCount = 0;
    constructor(name){
        this.name = name;
        this.amt = 0;
        this.cur = "INR";
        this.loc = "INDIA";
        this.id = Expense.expenseCount;

        // WILL NEED AT THE TIME OF REMOVING AN EXPENSE
        // COZ ALSO NEED TO REMOVE FROM THE ARRAY OF CATEGORY
        this.category;

        Expense.expenseCount++;
    }


    // EDIT HANDLERS

    handleNameEdit(e) {
        let newName = e.target.textContent;
        if(newName != this.name)
            this.name = newName;
    }

    handleAmountEdit(e) {
        this.amt = e.target.value;
    }

    handleCurrencyEdit(e) {
        this.cur = e.target.value;
    }

    handleLocationEdit(e) {
        this.loc = e.target.value;
    }

    removeExpense = () => {
        if(!confirm("Are you sure?")) return;
        // FINDING FROM DOM
        const expenseElement = document.querySelector(`.expense[data-expense-id="${this.id}"]`);

        if(expenseElement){
            expenseElement.parentElement.removeChild(expenseElement);

            const expenseIndex = this.category.expenses.indexOf(this);
            
            if (expenseIndex !== -1) {
                // Remove the expense from the array
                this.category.expenses.splice(expenseIndex, 1);
            } else {
                console.error("Expense not found in array.");
            }
        }

        if(confirm("Do you also want to remove it from the basic structure?")){
            console.log(this.category.name);
            console.log(this.name);
            let url = `/remove-expense/${this.category.name}?expense=${this.name}`;
            console.log(url);

            fetch(url).then(function (response) {
                // Waiting for response
                if (!response.ok)
                    throw new Error('Error while getting customer data from API: Network response was not OK');
                return response.text();
            }).then(function (data) {
                // Processing response
                console.log(data);
            });
        }
    }

    getAsElement(){
        /**
         * Returns DOM Object for the expense
         */

        // MAIN DIV
        let expenseDiv = createElementWithClassName("div", "expense");
        expenseDiv.setAttribute("data-expense-id", this.id);


        // P TAG (EXPENSE TITLE)
        let expenseTitle = createElementWithClassName("p", "expense-title");
        expenseTitle.innerText = this.name;
        expenseTitle.ondblclick = () => {
            expenseTitle.contentEditable = true;
            expenseTitle.focus();
        }
        expenseTitle.onblur = e => {
            expenseTitle.contentEditable = false;
            this.handleNameEdit(e);
        }
        expenseDiv.appendChild(expenseTitle);


        // AMOUNT INPUT
        let amountInput = createElementWithClassName("input", "amount-input");
        amountInput.type = "number";
        amountInput.value = this.amt;
        amountInput.onchange = e => {this.handleAmountEdit(e)}
        expenseDiv.appendChild(amountInput);


        // CURRENCY SELECT
        let currencySelect = createElementWithClassName("select", "currency-select");
        currencySelect.appendChild(getSelectOption("INR"));
        currencySelect.appendChild(getSelectOption("USD"));
        currencySelect.appendChild(getSelectOption("GBP"));
        currencySelect.appendChild(getSelectOption("EUR"));
        currencySelect.value = this.cur;
        currencySelect.onchange = e => {this.handleCurrencyEdit(e)}
        expenseDiv.appendChild(currencySelect);


        // LOCATION SELECT
        let locationSelect = createElementWithClassName("select", "location-select");
        locationSelect.appendChild(getSelectOption("INDIA"));
        locationSelect.appendChild(getSelectOption("USA"));
        locationSelect.appendChild(getSelectOption("GERMANY"));
        locationSelect.appendChild(getSelectOption("UK"));
        locationSelect.value = this.loc;
        locationSelect.onchange = e => {this.handleLocationEdit(e)}
        expenseDiv.appendChild(locationSelect);

        // REMOVE BTN
        let removeBtn = createElementWithClassName("a", "remove");
        
        let delete_img = document.createElement("img");
        delete_img.src = delete_img_path;

        removeBtn.appendChild(delete_img);

        removeBtn.onclick = this.removeExpense;
        expenseDiv.appendChild(removeBtn);

        return expenseDiv;
    }

    toJSON(){
        return{
            name: this.name,
            amt: this.amt,
            cur: this.cur,
            loc: this.loc,
            id: this.id
        }
    }
}

class Category{
    static container = null;
    constructor(name){
        if(container){
            this.name = name;
            this.expenses = [];
            this.DOM = this.getBasicCategoryHtml();
            this.DOMContent = this.DOM.querySelector(".content");
            container.appendChild(this.DOM);
        }else{
            console.error("container not assigned");
        }
    }

    removeCategory = () => {
        if(!confirm("Are you sure?")){
            this.DOM.querySelector(".title").click();
            return;
        }
        let category_index = categories.indexOf(this);
        if(category_index >= 0){
            categories.splice(category_index, 1);
            this.DOM.remove();

            if(confirm("Do you want to remove this category permanently?")){
                fetch(`/remove-category?name=${this.name}`).then(function (response) {
                    // Waiting for response
                    if (!response.ok)
                        throw new Error('Error while getting customer data from API: Network response was not OK');
                    return response.text();
                }).then(function (data) {
                    // Processing response
                    if(data == "success"){
                        alert("Category removed permanently");
                    }
                });
            }
        }
    }

    getBasicCategoryHtml(){
        let categoryDiv = createElementWithClassName("div", "category");
        
        let collapse_btn = document.createElement("div");
        collapse_btn.className = "collapse-btn";

        let titleDiv = createElementWithClassName("div", "title");
        titleDiv.onclick = () => {
            categoryDiv.classList.toggle("open");
        }
        let h3 = document.createElement("h3");
        h3.innerText = this.name;
        titleDiv.appendChild(h3);

        let delete_img = document.createElement("img");
        delete_img.src = delete_img_path;


        let deleteBtn = createElementWithClassName("a", "remove-cat-btn");
        deleteBtn.appendChild(delete_img);
        deleteBtn.onclick = this.removeCategory;

        
        let right = document.createElement("div");
        right.className = "right";
        right.appendChild(deleteBtn);
        right.appendChild(collapse_btn);

        titleDiv.appendChild(right);
        categoryDiv.appendChild(titleDiv);

        let addBtn = createElementWithClassName("a", "add-expense");
        addBtn.innerText = "Add new expense";
        addBtn.onclick = this.newExpenseFromUser;

        let contentDiv = createElementWithClassName("div", "content");
        contentDiv.appendChild(addBtn);
        categoryDiv.appendChild(contentDiv);

        return categoryDiv;
    }

    addExpenseToBase(expenseName){
        let url = `/add-expense/${this.name}?expense=${expenseName}`;
        console.log(url);

        fetch(url).then(function (response) {
            // Waiting for response
            if (!response.ok)
                throw new Error('Error while getting customer data from API: Network response was not OK');
            return response.text();
        }).then(function (data) {
            // Processing response
            console.log(data);
        });
    }

    newExpenseFromUser = () => {
        console.log(this);
        let expenseName = prompt("Enter expense name");

        if(expenseName && expenseName.length > 0)
            this.addExpense({name: expenseName});

        if(confirm("Do you want to add this expense permanently? If you add permanently, this expense will be shown to you every time you add new data.")){
            this.addExpenseToBase(expenseName);
        }
    }

    addExpense(obj){
        if(obj.name){
            // Atleast name must be defined
            let expense = new Expense(obj.name);

            // if obj defines a property, it should be assigned rather than the default one
            expense.amt = obj.amt ? obj.amt : expense.amt;
            expense.cur = obj.cur ? obj.cur : expense.cur;
            expense.loc = obj.loc ? obj.loc : expense.loc;

            expense.category = this;
            this.expenses.push(expense);

            let addBtn = this.DOMContent.querySelector(".add-expense");
            this.DOMContent.insertBefore(expense.getAsElement(), addBtn);
        }else{
            console.error("Bad Reference object passed to addExpense");
        }
    }

    toJSON(){
        // OVERRIDING THIS METHOD TO HIDE DOM FROM JSON

        return {
            name: this.name,
            expenses: this.expenses
        };
    }
}

let baseData = {}

fetch("/get-base").then(function (response) {
    // Waiting for response
    if (!response.ok)
        throw new Error('Error while getting customer data from API: Network response was not OK');
    return response.json();
}).then(function (data) {
    // Processing response
    console.log(data);
    baseData = data;
    console.log("assigned");
    populate_categories();
});

function formatDateToMON_YY() {
    const months = [
      "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
      "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ];

    let date = new Date();
  
    const year = date.getFullYear() % 100;
    const month = months[date.getMonth()];
    
    return `${month}_${year.toString().padStart(2, '0')}`;
}

function new_category(){
    let name = prompt("Enter category name");
    if(name && name.length > 0){
        let category = new Category(name);
        categories.push(category);
        
        if(confirm("Do you want to add this category permanently?")){
            fetch(`/add-category?name=${name}`).then(function (response) {
                // Waiting for response
                if (!response.ok)
                    throw new Error('Error while getting customer data from API: Network response was not OK');
                return response.text();
            }).then(function (data) {
                // Processing response
                if(data == "success"){
                    alert("Category added permanently. Every time you enter new data, this category will be added automatically");
                }
            });
        }else{
            alert("This category is added temporarily. The next time you enter data, this category will NOT be shown by default.");
        }
    }
}

function submit_data(){
    let income_val = document.querySelector("#income-input").value;
    if(income_val == ''){
        alert("Income Required");
        return;
    }
    let dummy_data = {
        date: formatDateToMON_YY(),
        username: document.querySelector("#username-input").value,
        income: income_val,
        categories: categories
    };
    console.log(JSON.stringify(dummy_data));
    let url = "/insert?data=" + JSON.stringify(dummy_data);
    fetch(url).then(function (response) {
        // Waiting for response
        if (!response.ok)
            throw new Error('Error while getting customer data from API: Network response was not OK');
        return response.text();
    }).then(function (data) {
        // Processing response
        console.log(data);
        if(data == "Data inserted"){
            alert("Data Inserted!");
            window.location.href = "/";
        }else{
            alert("Something happend and data could not be entered!");
        }
    });
}

let dateField = document.querySelector("#date-field");

dateField.innerText = formatDate(formatDateToMON_YY());

const categories = [];
const container = document.querySelector(".container");

// Populating static container attr.
Category.parent = container;

function populate_categories(){
// ADDING BASE DATA CATEGORIES
    for(const category_name in baseData.categories){
        const expenses = baseData.categories[category_name];

        let category = new Category(category_name);
        categories.push(category);

        expenses.forEach(expense => {
            category.addExpense(expense);
        });
    }
}