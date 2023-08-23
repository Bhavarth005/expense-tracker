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
        console.log(`Removing ${this.id}`);
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
        removeBtn.innerText = "Remove";
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

    getBasicCategoryHtml(){
        let categoryDiv = createElementWithClassName("div", "category");
        

        let titleDiv = createElementWithClassName("div", "title");
        titleDiv.onclick = () => {
            categoryDiv.classList.toggle("open");
        }
        let h3 = document.createElement("h3");
        h3.innerText = this.name;
        titleDiv.appendChild(h3);
        categoryDiv.appendChild(titleDiv);

        let addBtn = createElementWithClassName("a", "add-expense");
        addBtn.innerText = "Add new expense";
        addBtn.onclick = this.newExpenseFromUser;

        let contentDiv = createElementWithClassName("div", "content");
        contentDiv.appendChild(addBtn);
        categoryDiv.appendChild(contentDiv);

        return categoryDiv;
    }

    newExpenseFromUser = () => {
        console.log(this);
        let expenseName = prompt("Enter expense name");

        if(expenseName && expenseName.length > 0)
            this.addExpense({name: expenseName});
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

let baseData = {
    categories: {
        Servers:[
            {
                name: "AWS",
                amt: 100,
                cur: 'USD',
                loc: 'USA'
            },
            {
                name: "Google Cloud Services",
                amt: 300,
                cur: 'EUR',
                loc: 'UK'
            }
        ],
        Services:[
            {
                name: "Cloudflare",
                amt: 10,
                cur: 'USD',
                loc: 'USA'
            },
            {
                name: "CPanel",
                amt: 8,
                cur: 'EUR',
                loc: 'EUROPE'
            }
        ]
    }
}

function new_category(){
    let name = prompt("Enter category name");
    if(name && name.length > 0){
        let category = new Category(name);
        categories.push(category);
    }
}

const categories = [];
const container = document.querySelector(".container");
Category.parent = container;
// ADDING BASE DATA CATEGORIES

for(const category_name in baseData.categories){
    const expenses = baseData.categories[category_name];

    let category = new Category(category_name);
    categories.push(category);

    expenses.forEach(expense => {
        category.addExpense(expense);
    });
}