import { Selector } from 'testcafe';
import { request } from './util';

fixture(`Landing Page`).beforeEach(async (test) => {
    await request('http://localhost:6543/tests');
    await test
        .navigateTo('http://localhost:6543/')
        .resizeWindow(1024, 768);
});

test('Has the app title', async (test) => {
    await test
        .expect(Selector('h1').filterVisible().innerText).eql('Senior Common Room')
        .expect(Selector('h2').filterVisible().innerText).eql('Senior Common Room - Login');
});

test('Check warning on small screens', async (test) => {
    await test
        .resizeWindow(800, 600)
        .expect(Selector('h2').filterVisible().innerText).eql('Display unsupported');
});
