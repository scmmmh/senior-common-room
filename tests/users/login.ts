import { Selector } from 'testcafe';
import { request } from '../util';

fixture(`User Login`).beforeEach(async (test) => {
    await request('http://localhost:6543/tests?obj=user1');
    await test
        .navigateTo('http://localhost:6543/')
        .resizeWindow(1024, 768);
});

test('Successful login', async (test) => {
    await test
        .expect(Selector('h1').filterVisible().innerText).eql('Senior Common Room')
        .expect(Selector('h2').filterVisible().innerText).eql('Senior Common Room - Login')
        .typeText(Selector('label').withText('E-Mail').find('input'), 'test1@example.com')
        .typeText(Selector('label').withText('Password').find('input'), 'test')
        .click(Selector('button').withText('Log in'))
        .expect(Selector('h2').withText('Senior Common Room - Login').filterVisible().exists).notOk()
        .expect(Selector('h2').withText('Senior Common Room - Authenticating').filterVisible().exists).notOk();
});

test('Failed login - email', async (test) => {
    await test
        .expect(Selector('h1').filterVisible().innerText).eql('Senior Common Room')
        .expect(Selector('h2').filterVisible().innerText).eql('Senior Common Room - Login')
        .typeText(Selector('label').withText('E-Mail').find('input'), 'test2@example.com')
        .typeText(Selector('label').withText('Password').find('input'), 'test')
        .click(Selector('button').withText('Log in'))
        .expect(Selector('h2').withText('Senior Common Room - Authenticating').filterVisible().exists).notOk()
        .expect(Selector('span.error').withText('E-Mail or password incorrect.').exists).ok();
});

test('Failed login - password', async (test) => {
    await test
        .expect(Selector('h1').filterVisible().innerText).eql('Senior Common Room')
        .expect(Selector('h2').filterVisible().innerText).eql('Senior Common Room - Login')
        .typeText(Selector('label').withText('E-Mail').find('input'), 'test1@example.com')
        .typeText(Selector('label').withText('Password').find('input'), 'testing')
        .click(Selector('button').withText('Log in'))
        .expect(Selector('h2').withText('Senior Common Room - Authenticating').filterVisible().exists).notOk()
        .expect(Selector('span.error').withText('E-Mail or password incorrect.').exists).ok();
});
